#!/usr/bin/env python3
"""Railway-ready Twitter News Bot service."""

import asyncio
import json
import logging
import os
import tempfile
import textwrap
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
import tweepy  # type: ignore
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, Field
from PIL import Image, ImageDraw, ImageFont
from tweepy.errors import Forbidden  # type: ignore[attr-defined]

try:
    from pyppeteer import launch  # type: ignore
except ImportError:  # pragma: no cover
    launch = None  # type: ignore

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger("twitter_news_bot")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class TwitterNewsBot:
    """Python adaptation of the TypeScript twitter-news-bot."""

    CRYPTO_SYMBOLS = [
        "BTC",
        "ETH",
        "SOL",
        "XRP",
        "ADA",
        "DOT",
        "MATIC",
        "LINK",
        "UNI",
        "AVAX",
    ]

    COINGECKO_IDS = ["bitcoin", "ethereum", "solana", "ripple", "cardano"]

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        logger.debug("Initialising TwitterNewsBot with config keys: %s", list(config.keys()))

        self.twitter_client = tweepy.Client(
            consumer_key=config["twitter_api_key"],
            consumer_secret=config["twitter_api_secret"],
            access_token=config["twitter_access_token"],
            access_token_secret=config["twitter_access_secret"],
        )

        auth = tweepy.OAuth1UserHandler(
            config["twitter_api_key"],
            config["twitter_api_secret"],
            config["twitter_access_token"],
            config["twitter_access_secret"],
        )
        self.twitter_api = tweepy.API(auth)

        self.openai_client = OpenAI(api_key=config["openai_api_key"])
        logger.debug("TwitterNewsBot initialised successfully")

    # ------------------------------------------------------------------
    # News fetching helpers
    # ------------------------------------------------------------------
    def fetch_crypto_news(self) -> List[Dict[str, str]]:
        items: List[Dict[str, str]] = []
        logger.debug("Fetching crypto news")
        try:
            response = requests.get(
                "https://cryptopanic.com/api/v1/posts/",
                params={"auth_token": "free", "kind": "news", "filter": "important"},
                timeout=10,
            )
            response.raise_for_status()
            payload = response.json()
            logger.debug("Received %s crypto items from CryptoPanic", len(payload.get("results", [])))
            for entry in payload.get("results", [])[:5]:
                items.append(
                    {
                        "title": entry["title"],
                        "description": entry["title"],
                        "url": entry["url"],
                        "published_at": entry["published_at"],
                        "source": entry["source"]["title"],
                    }
                )
        except Exception as exc:  # pragma: no cover - network fallback
            logger.warning("Crypto news fetch failed, falling back to CoinGecko: %s", exc)
            try:
                response = requests.get(
                    "https://api.coingecko.com/api/v3/search/trending", timeout=10
                )
                response.raise_for_status()
                fallback_payload = response.json()
                logger.debug("CoinGecko trending returned %s coins", len(fallback_payload.get("coins", [])))
                for coin in fallback_payload.get("coins", [])[:5]:
                    item = coin["item"]
                    items.append(
                        {
                            "title": f"{item['name']} ({item['symbol']}) is trending",
                            "description": f"Market Cap Rank: #{item['market_cap_rank']}",
                            "url": f"https://www.coingecko.com/en/coins/{item['id']}",
                            "published_at": datetime.utcnow().isoformat(),
                            "source": "CoinGecko",
                        }
                    )
            except Exception as fallback_error:  # pragma: no cover
                logger.error("Fallback crypto news failed: %s", fallback_error)
        logger.debug("Returning %s crypto news items", len(items))
        return items

    def fetch_world_news(self) -> List[Dict[str, str]]:
        items: List[Dict[str, str]] = []
        api_key = self.config.get("news_api_key")
        if api_key and api_key != "demo":
            logger.debug("Fetching world news via NewsAPI")
            try:
                response = requests.get(
                    "https://newsapi.org/v2/top-headlines",
                    params={
                        "apiKey": api_key,
                        "category": "technology",
                        "language": "en",
                        "pageSize": 5,
                    },
                    timeout=10,
                )
                response.raise_for_status()
                articles_payload = response.json()
                logger.debug("NewsAPI returned %s articles", len(articles_payload.get("articles", [])))
                for article in articles_payload.get("articles", [])[:5]:
                    items.append(
                        {
                            "title": article.get("title"),
                            "description": article.get("description") or article.get("title"),
                            "url": article.get("url"),
                            "published_at": article.get("publishedAt"),
                            "source": article.get("source", {}).get("name", "News"),
                        }
                    )
            except Exception as exc:  # pragma: no cover - fallback path
                logger.warning("World news fetch via NewsAPI failed: %s", exc)

        if not items:
            logger.debug("Falling back to HackerNews for world news")
            try:
                top_ids = requests.get(
                    "https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10
                ).json()[:5]
                logger.debug("HackerNews top stories IDs: %s", top_ids)
                for story_id in top_ids:
                    story = requests.get(
                        f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                        timeout=10,
                    ).json()
                    items.append(
                        {
                            "title": story.get("title", ""),
                            "description": story.get("title", ""),
                            "url": story.get("url")
                            or f"https://news.ycombinator.com/item?id={story_id}",
                            "published_at": datetime.utcfromtimestamp(story.get("time", 0)).isoformat(),
                            "source": "HackerNews",
                        }
                    )
            except Exception as exc:  # pragma: no cover
                logger.error("Fallback world news failed: %s", exc)
        logger.debug("Returning %s world news items", len(items))
        return items

    # ------------------------------------------------------------------
    # AI helpers
    # ------------------------------------------------------------------
    def summarize_news(self, news_items: List[Dict[str, str]]) -> Tuple[str, List[str]]:
        logger.debug("Summarising %s news items", len(news_items))
        if not news_items:
            return "Latest news update", ["Stay informed"]

        news_text = "\n".join(
            f"{i+1}. {item['title']}\nSource: {item['source']}" for i, item in enumerate(news_items)
        )

        prompt = (
            "Analyze these crypto/tech news discoveries and respond using the format:\n"
            "HEADLINE: BREAKING TOP OF THE HOUR: ... (max 100 chars)\n"
            "KEY POINTS:\n"
            "• point 1\n• point 2\n• point 3\n"
            "Each key point max 100 characters. End the last bullet with 'Powered by 0xQuantAi Agent - The Future of Crypto Action'.\n\n"
            f"News items:\n{news_text}\n"
        )

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a top crypto influencer who writes punchy Twitter content."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,
                temperature=0.7,
            )
            content = response.choices[0].message.content or ""
        except OpenAIError as exc:  # pragma: no cover - network
            logger.error("OpenAI summary failure: %s", exc)
            headline = news_items[0]["title"]
            points = [item["title"] for item in news_items[1:4]] or ["Stay informed"]
            return headline, points

        logger.debug("Raw summary response: %s", content)
        headline = ""
        key_points: List[str] = []
        for line in content.splitlines():
            if line.startswith("HEADLINE:"):
                headline = line.split("HEADLINE:", 1)[1].strip()
            elif line.strip().startswith("•"):
                key_points.append(line.strip("• "))

        if not headline:
            headline = news_items[0]["title"]
        if not key_points:
            key_points = [item["title"] for item in news_items[:3]]

        key_points = key_points[:3]
        logger.debug("Parsed headline: %s", headline)
        logger.debug("Parsed key points: %s", key_points)
        return headline, key_points

    def _get_font(self, font_name: str, size: int, bold: bool = False) -> Optional[ImageFont.FreeTypeFont]:
        """Try to load a font, fallback to default if not found."""
        font_paths = {
            "Inter": [
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            ],
            "Montserrat": [
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            ],
            "Roboto": [
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            ],
            "HelveticaNeue": [
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Supplemental/Arial.ttf",
            ],
        }
        
        paths = font_paths.get(font_name, font_paths["Inter"])
        if bold:
            paths = [p.replace(".ttf", "-Bold.ttf").replace(".ttc", "-Bold.ttc") for p in paths] + paths
        
        for path in paths:
            if Path(path).exists():
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue
        
        # Fallback to default font
        try:
            return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", size)
        except Exception:
            return ImageFont.load_default()

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Wrap text to fit within max_width pixels."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines if lines else [text]

    def _draw_bitcoin_logo(self, draw: ImageDraw.Draw, x: int, y: int, size: int):
        """Draw a simple Bitcoin logo (B symbol with lines)."""
        # Draw circular background (light beige/off-white)
        circle_radius = size // 2
        circle_color = (245, 245, 240)  # Light beige/off-white
        draw.ellipse(
            [x - circle_radius, y - circle_radius, x + circle_radius, y + circle_radius],
            fill=circle_color
        )
        
        # Draw "B" symbol in black
        b_color = (0, 0, 0)
        b_font_size = int(size * 0.7)
        b_font = self._get_font("HelveticaNeue", b_font_size, bold=True)
        if b_font:
            b_bbox = b_font.getbbox("B")
            b_width = b_bbox[2] - b_bbox[0]
            b_height = b_bbox[3] - b_bbox[1]
            b_x = x - b_width // 2
            b_y = y - b_height // 2
            draw.text((b_x, b_y), "B", font=b_font, fill=b_color)
        
        # Draw two horizontal lines through the B
        line_color = (0, 0, 0)
        line_width = 3
        line_y1 = y - int(size * 0.15)
        line_y2 = y + int(size * 0.15)
        line_x_start = x - int(size * 0.4)
        line_x_end = x + int(size * 0.4)
        draw.line([(line_x_start, line_y1), (line_x_end, line_y1)], fill=line_color, width=line_width)
        draw.line([(line_x_start, line_y2), (line_x_end, line_y2)], fill=line_color, width=line_width)

    def _extract_hashtags(self, headline: str, key_points: List[str]) -> str:
        """Extract relevant hashtags from content."""
        hashtags = []
        text = f"{headline} {' '.join(key_points)}".upper()
        
        # Common crypto hashtags
        crypto_keywords = {
            "BITCOIN": "#Bitcoin", "BTC": "#Bitcoin",
            "ETHEREUM": "#Ethereum", "ETH": "#Ethereum",
            "SOLANA": "#Solana", "SOL": "#Solana",
            "ZCASH": "#Zcash", "ZEC": "#Zcash",
            "FIRO": "#Firo",
            "MONERO": "#Monero", "XMR": "#Monero",
            "NEAR": "#NEAR", "NEAR PROTOCOL": "#NEAR",
            "UNISWAP": "#Uniswap", "UNI": "#Uniswap",
            "NFT": "#NFTs", "NFTs": "#NFTs", "PENGUIN": "#NFTs",
            "WEB3": "#Web3",
        }
        
        # Check for crypto keywords
        for keyword, hashtag in crypto_keywords.items():
            if keyword in text and hashtag not in hashtags:
                hashtags.append(hashtag)
        
        # Add default hashtags if none found
        if not hashtags:
            hashtags = ["#Crypto", "#Tech", "#News"]
        elif len(hashtags) < 3:
            # Add Web3 or NFTs if relevant
            if "NFT" in text or "PENGUIN" in text:
                if "#NFTs" not in hashtags:
                    hashtags.append("#NFTs")
            if "WEB3" in text or "BLOCKCHAIN" in text:
                if "#Web3" not in hashtags:
                    hashtags.append("#Web3")
            # Fill remaining slots
            defaults = ["#Crypto", "#Tech", "#News"]
            for default in defaults:
                if len(hashtags) < 3 and default not in hashtags:
                    hashtags.append(default)
        
        return " ".join(hashtags[:3])  # Max 3 hashtags

    def generate_ai_image(self, headline: str, key_points: List[str]) -> Optional[str]:
        """Generate news card with text overlay using Pillow - matching image 2 style."""
        logger.debug("Generating text overlay image with headline: %s", headline)
        
        # Ensure headline starts with "BREAKING TOP OF THE HOUR:" if not already present
        formatted_headline = headline
        if not headline.upper().startswith("BREAKING TOP OF THE HOUR"):
            formatted_headline = f"BREAKING TOP OF THE HOUR: {headline}"
        
        # Use all key points as bullet points (no limit for image)
        bullet_points = key_points if key_points else ["Latest crypto and tech updates."]
        
        # Extract hashtags from content
        hashtags = self._extract_hashtags(headline, key_points)
        
        # Canvas dimensions
        width, height = 1200, 675
        
        # Try multiple font variations
        font_variations = ["Inter", "Montserrat", "Roboto", "HelveticaNeue"]
        temp_dir = Path(tempfile.gettempdir()) / "twitter_bot"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        for font_name in font_variations:
            try:
                # Load placeholder background image if available, otherwise use solid color
                # Check environment variable, config, or default to template.png in bot directory
                placeholder_path = (
                    os.getenv("PLACEHOLDER_IMAGE_PATH") 
                    or self.config.get("placeholder_image_path")
                    or str(Path(__file__).parent / "template.png")
                )
                img = None
                
                if placeholder_path and os.path.exists(placeholder_path):
                    try:
                        logger.debug("Loading placeholder image from: %s", placeholder_path)
                        img = Image.open(placeholder_path)
                        # Convert to RGB if necessary (handles RGBA, P, etc.)
                        if img.mode != "RGB":
                            img = img.convert("RGB")
                        # Resize to match canvas dimensions (1200x675)
                        img = img.resize((width, height), Image.LANCZOS)
                        logger.debug("Placeholder image loaded and resized successfully")
                    except Exception as exc:
                        logger.warning("Failed to load placeholder image, using solid color background: %s", exc)
                        img = None
                
                # Fallback to solid color background if placeholder not available
                if img is None:
                    img = Image.new("RGB", (width, height), color=(30, 30, 30))  # Dark grey/black
                
                draw = ImageDraw.Draw(img)
                
                # Font sizes (larger for headline and bullet points)
                headline_font = self._get_font(font_name, 52, bold=True)
                bullet_font = self._get_font(font_name, 38, bold=False)  # Increased from 24 to 28
                hashtag_font = self._get_font(font_name, 20, bold=False)
                footer_font = self._get_font(font_name, 26, bold=True)  # Footer font
                
                # Colors (white text)
                text_color = (255, 255, 255)  # White
                hashtag_color = (255, 255, 255)  # White
                footer_color = (180, 180, 180)  # Light gray for footer
                
                # Padding
                padding_x = 60
                padding_y = 50
                content_width = width - (2 * padding_x) - 150  # Leave space for logo on right
                
                # Footer text
                footer_text = "Powered by 0xQuant Agent"
                footer_height = footer_font.getbbox(footer_text)[3] - footer_font.getbbox(footer_text)[1]
                
                # Draw headline (top) - allow multiple lines
                headline_lines = self._wrap_text(formatted_headline, headline_font, content_width)
                y_position = padding_y
                
                for line in headline_lines:
                    bbox = headline_font.getbbox(line)
                    text_width = bbox[2] - bbox[0]
                    x_position = padding_x  # Left align
                    draw.text((x_position, y_position), line, font=headline_font, fill=text_color)
                    y_position += bbox[3] - bbox[1] + 8  # Tighter spacing
                
                # Draw bullet points (middle section)
                y_position += 30  # Space after headline
                bullet_start_y = y_position
                
                # Calculate available space for bullet points (leave room for hashtags and footer at bottom)
                hashtag_height = hashtag_font.getbbox(hashtags)[3] - hashtag_font.getbbox(hashtags)[1]
                available_height = height - y_position - padding_y - hashtag_height - footer_height - 30  # 30px buffer for spacing
                
                # Fit as many bullet points as possible
                fitted_points = []
                current_height = 0
                
                for point in bullet_points:
                    point_lines = self._wrap_text(point, bullet_font, content_width)
                    point_height = sum(
                        (bullet_font.getbbox(line)[3] - bullet_font.getbbox(line)[1] + 12)
                        for line in point_lines
                    ) + 8  # Add spacing between points
                    
                    if current_height + point_height <= available_height:
                        fitted_points.append(point)
                        current_height += point_height
                    else:
                        # Try to fit at least part of the point if we have some space
                        if current_height < available_height - 50:  # At least 50px available
                            # Try to fit first line of this point
                            first_line = point_lines[0] if point_lines else point[:50]
                            first_line_height = bullet_font.getbbox(first_line)[3] - bullet_font.getbbox(first_line)[1] + 12
                            if current_height + first_line_height <= available_height:
                                fitted_points.append(first_line + "...")
                        break
                
                # Draw fitted bullet points
                for i, point in enumerate(fitted_points):
                    # Wrap bullet point text
                    point_lines = self._wrap_text(point, bullet_font, content_width)
                    
                    for j, line in enumerate(point_lines):
                        x_position = padding_x
                        bbox = bullet_font.getbbox(line)
                        draw.text((x_position, y_position), line, font=bullet_font, fill=text_color)
                        y_position += bbox[3] - bbox[1] + 12
                    
                    # Add spacing between bullet points
                    if i < len(fitted_points) - 1:
                        y_position += 8
                
                logger.debug("Fitted %s/%s bullet points in image", len(fitted_points), len(bullet_points))
                
                # Draw Bitcoin logo on the right side (aligned with bullet points)
                logo_size = 120
                logo_x = width - padding_x - logo_size // 2
                logo_y = bullet_start_y + (y_position - bullet_start_y) // 2  # Center vertically with bullet points
                self._draw_bitcoin_logo(draw, logo_x, logo_y, logo_size)
                
                # Draw hashtags (above footer)
                hashtag_bbox = hashtag_font.getbbox(hashtags)
                hashtag_width = hashtag_bbox[2] - hashtag_bbox[0]
                hashtag_x = padding_x  # Left align
                hashtag_y = height - padding_y - footer_height - 10 - (hashtag_bbox[3] - hashtag_bbox[1])  # 10px spacing above footer
                draw.text((hashtag_x, hashtag_y), hashtags, font=hashtag_font, fill=hashtag_color)
                
                # Draw footer (bottom)
                footer_bbox = footer_font.getbbox(footer_text)
                footer_width = footer_bbox[2] - footer_bbox[0]
                footer_x = padding_x  # Left align
                footer_y = height - padding_y - (footer_bbox[3] - footer_bbox[1])
                draw.text((footer_x, footer_y), footer_text, font=footer_font, fill=footer_color)
                
                # Save image
                image_path = temp_dir / f"news_overlay_{font_name.lower()}_{int(datetime.utcnow().timestamp())}.png"
                img.save(str(image_path), "PNG", optimize=True)
                logger.debug("Text overlay image saved: %s (font: %s)", image_path, font_name)
                
                # Return first successful variation
                return str(image_path)
                
            except Exception as exc:
                logger.warning("Failed to generate image with font %s: %s", font_name, exc, exc_info=True)
                continue
        
        logger.error("Failed to generate text overlay image with any font variation")
        return None

    async def _capture_screenshot(
        self, url: str, selector: Optional[str], width: int, height: int
    ) -> Optional[str]:
        logger.debug("Launching headless browser for screenshot: url=%s selector=%s", url, selector)
        if launch is None:
            logger.warning("pyppeteer is not installed; skipping screenshot generation")
            return None

        executable_path = (
            os.environ.get("CHROMIUM_PATH")
            or shutil.which("chromium")
            or shutil.which("chromium-browser")
            or shutil.which("google-chrome")
            or shutil.which("google-chrome-stable")
        )

        if not executable_path:
            logger.error(
                "Chromium executable not found. Set CHROMIUM_PATH environment variable "
                "or ensure chromium is available on PATH."
            )
            return None

        logger.debug("Using Chromium executable at: %s", executable_path)

        browser = await launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1200,800",
            ],
            handleSIGINT=False,
            handleSIGTERM=False,
            handleSIGHUP=False,
            executablePath=executable_path,
        )
        try:
            page = await browser.newPage()
            await page.setViewport({"width": width, "height": height, "deviceScaleFactor": 2})
            
            # Set user agent to avoid bot detection
            await page.setUserAgent(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            logger.debug("Navigating to %s", url)
            await page.goto(url, {"waitUntil": "networkidle2", "timeout": 30000})
            
            # Wait for page to be fully loaded
            await asyncio.sleep(3)
            
            # If selector provided, wait for it to appear and be visible
            if selector:
                logger.debug("Waiting for selector %s to appear", selector)
                # Try each selector if multiple provided (comma-separated)
                selectors = [s.strip() for s in selector.split(",")]
                selector_found = False
                for sel in selectors:
                    try:
                        await page.waitForSelector(sel, {"timeout": 5000, "visible": True})
                        logger.debug("Selector %s found and visible", sel)
                        selector = sel  # Use the first found selector
                        selector_found = True
                        break
                    except Exception:
                        logger.debug("Selector %s not found, trying next", sel)
                        continue
                
                if selector_found:
                    # Additional wait for dynamic content (charts, etc.)
                    await asyncio.sleep(3)
                else:
                    logger.warning("None of the selectors found: %s, will try viewport screenshot", selectors)

            temp_dir = Path(tempfile.gettempdir()) / "twitter_bot"
            temp_dir.mkdir(parents=True, exist_ok=True)
            image_path = temp_dir / f"screenshot_{int(datetime.utcnow().timestamp())}.png"

            screenshot_taken = False
            if selector:
                try:
                    element = await page.querySelector(selector)
                    if element:
                        # Check if element has dimensions
                        box = await page.evaluate(
                            f"""() => {{
                                const el = document.querySelector('{selector}');
                                if (!el) return null;
                                const rect = el.getBoundingClientRect();
                                return {{width: rect.width, height: rect.height}};
                            }}"""
                        )
                        if box and box.get("width", 0) > 0 and box.get("height", 0) > 0:
                            logger.debug("Capturing element screenshot for selector %s (size: %sx%s)", 
                                        selector, box.get("width"), box.get("height"))
                            await element.screenshot({"path": str(image_path)})
                            screenshot_taken = True
                        else:
                            logger.warning("Element %s has zero dimensions, falling back to viewport", selector)
                    else:
                        logger.warning("Element %s not found, falling back to viewport", selector)
                except Exception as element_error:
                    logger.warning("Element screenshot failed: %s, falling back to viewport", element_error)
            
            if not screenshot_taken:
                logger.debug("Capturing viewport screenshot")
                await page.screenshot({"path": str(image_path), "fullPage": False})
            
            # Verify screenshot was created and has content
            if image_path.exists():
                file_size = image_path.stat().st_size
                logger.debug("Screenshot stored at %s (size: %s bytes)", image_path, file_size)
                if file_size < 1000:  # Less than 1KB is likely empty/corrupt
                    logger.error("Screenshot file is suspiciously small (%s bytes), may be empty", file_size)
                    return None
                return str(image_path)
            else:
                logger.error("Screenshot file was not created at %s", image_path)
                return None
                
        except Exception as exc:  # pragma: no cover
            logger.error("Screenshot capture failed: %s", exc, exc_info=True)
            return None
        finally:
            await browser.close()
            logger.debug("Browser closed")

    def _download_chart_image(self, symbol: str, days: int = 7) -> Optional[str]:
        """Download chart image directly from CoinGecko API (no CAPTCHA)."""
        try:
            # Map symbol to CoinGecko ID
            symbol_to_id = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                "SOL": "solana",
                "XRP": "ripple",
                "ADA": "cardano",
                "DOT": "polkadot",
                "MATIC": "matic-network",
                "LINK": "chainlink",
                "UNI": "uniswap",
                "AVAX": "avalanche-2",
            }
            coin_id = symbol_to_id.get(symbol.upper(), "bitcoin")
            
            # Use CoinGecko's public chart image endpoint (returns PNG)
            # Format: https://www.coingecko.com/coins/{id}/sparkline.png
            chart_image_url = f"https://www.coingecko.com/coins/{coin_id}/sparkline.png"
            logger.debug("Downloading chart PNG from CoinGecko: %s", chart_image_url)
            
            response = requests.get(chart_image_url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "image/png,image/*,*/*;q=0.8",
                "Referer": "https://www.coingecko.com/",
            })
            
            if response.status_code == 200 and response.content and len(response.content) > 1000:
                temp_dir = Path(tempfile.gettempdir()) / "twitter_bot"
                temp_dir.mkdir(parents=True, exist_ok=True)
                image_path = temp_dir / f"chart_{symbol}_{int(datetime.utcnow().timestamp())}.png"
                image_path.write_bytes(response.content)
                logger.debug("Chart PNG downloaded to %s (%s bytes)", image_path, len(response.content))
                return str(image_path)
            else:
                logger.warning("Chart image download failed: status %s, size %s", 
                             response.status_code, len(response.content) if response.content else 0)
                return None
        except Exception as exc:
            logger.error("Chart image download failed: %s", exc, exc_info=True)
            return None

    def generate_screenshot(self, news_items: List[Dict[str, str]], target: str) -> Optional[str]:
        logger.debug("Generating screenshot (target=%s)", target)
        
        target = target or "crypto-chart"
        if target == "crypto-chart":
            symbol = "BTC"
            for item in news_items:
                combined = f"{item['title']} {item['description']}".upper()
                for sym in self.CRYPTO_SYMBOLS:
                    if sym in combined:
                        symbol = sym
                        break
                if symbol != "BTC":
                    break
            
            # Try direct chart image download first (no CAPTCHA)
            logger.debug("Attempting direct chart image download for %s", symbol)
            chart_image = self._download_chart_image(symbol)
            if chart_image:
                return chart_image
            
            # Fallback to browser screenshot if direct download fails
            logger.debug("Direct download failed, falling back to browser screenshot")
            if launch is None:
                logger.warning("pyppeteer not installed; screenshot disabled")
                return None
            
            # Use a simpler chart service that's less likely to have CAPTCHA
            # Use CoinMarketCap or a public chart API
            url = f"https://coinmarketcap.com/currencies/{symbol.lower()}/"
            selector = ".cmc-chart-container, .price-chart-container, canvas"
            width, height = 1200, 600
            logger.debug("Using CoinMarketCap chart for %s at %s", symbol, url)
            
        elif target == "crypto-ticker":
            symbol = "bitcoin"
            for item in news_items:
                combined = f"{item['title']} {item['description']}".lower()
                for sym in self.COINGECKO_IDS:
                    if sym in combined:
                        symbol = sym
                        break
                if symbol != "bitcoin":
                    break
            
            if launch is None:
                logger.warning("pyppeteer not installed; screenshot disabled")
                return None
            
            url = f"https://www.coingecko.com/en/coins/{symbol}"
            selector = ".gecko-coin-detail-header"
            width, height = 1200, 400
        else:  # news-article
            if launch is None:
                logger.warning("pyppeteer not installed; screenshot disabled")
                return None
            
            url = news_items[0].get("url") or "https://news.ycombinator.com"
            selector = "article, main, .article-content, .post-content"
            width, height = 1200, 800

        logger.debug("Screenshot configuration resolved: url=%s selector=%s", url, selector)
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            return asyncio.run_coroutine_threadsafe(
                self._capture_screenshot(url, selector, width, height), loop
            ).result()

        return asyncio.run(self._capture_screenshot(url, selector, width, height))

    # ------------------------------------------------------------------
    # Upload / Twitter helpers
    # ------------------------------------------------------------------
    def upload_to_uploadme(self, media_path: str) -> Optional[str]:
        api_key = self.config.get("uploadme_api_key")
        if not api_key or not Path(media_path).exists():
            return None
        try:
            with open(media_path, "rb") as file_handle:
                data = {
                    "key": api_key,
                    "format": "json",
                }
                files = {"source": file_handle}
                response = requests.post(
                    "https://uploadme.me/api/1/upload", data=data, files=files, timeout=30
                )
            response.raise_for_status()
            payload = response.json()
            return payload.get("image", {}).get("url") or payload.get("URL")
        except Exception as exc:  # pragma: no cover
            print("UploadMe upload failed:", exc)
            return None

    def post_tweet(self, text: str, media_path: Optional[str]) -> Dict[str, Any]:
        image_url: Optional[str] = None
        final_text = text

        logger.debug("Posting tweet (dry_run=%s) media_path=%s", False, media_path)
        if media_path and Path(media_path).exists():
            try:
                media = self.twitter_api.media_upload(media_path)
                response = self.twitter_client.create_tweet(
                    text=text, media_ids=[media.media_id]
                )
                Path(media_path).unlink(missing_ok=True)
                logger.info("Tweet posted with media: id=%s", response.data.get("id"))
                return {
                    "success": True,
                    "tweetId": response.data.get("id"),
                    "tweetText": text,
                    "imageUrl": image_url,
                }
            except Forbidden as exc:
                logger.warning("Direct media upload failed, attempting UploadMe fallback: %s", exc)
                image_url = self.upload_to_uploadme(media_path)
                Path(media_path).unlink(missing_ok=True)
                if image_url:
                    available = 280 - len(image_url) - 1
                    if len(final_text) > available:
                        final_text = final_text[: available - 3] + "..."
                    final_text = f"{final_text}\n{image_url}"
                else:
                    logger.error("UploadMe fallback failed; posting text only")
            except Exception as exc:  # pragma: no cover
                logger.error("Media upload failed: %s", exc)
                Path(media_path).unlink(missing_ok=True)

        response = self.twitter_client.create_tweet(text=final_text)
        logger.info("Tweet posted without media: id=%s", response.data.get("id"))
        return {
            "success": True,
            "tweetId": response.data.get("id"),
            "tweetText": final_text,
            "imageUrl": image_url,
        }

    # ------------------------------------------------------------------
    # Main runner
    # ------------------------------------------------------------------
    def build_tweet_text(self, headline: str, key_points: List[str]) -> Tuple[str, str]:
        key_points = key_points[:3]
        headline = headline.strip()

        full_format = "📰 " + headline + "\n\n" + "\n".join("▸ " + p for p in key_points) + "\n\n"
        abbreviated = "📰 " + headline + "\n\n" + ("▸ " + key_points[0] if key_points else "") + "\n\n"
        minimal = "📰 " + headline + "\n\n"

        if len(full_format) <= 260:
            return full_format.strip(), "full"
        if len(abbreviated) <= 280:
            return abbreviated.strip(), "abbreviated"
        return minimal.strip(), "minimal"

    def run(self, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        opts = {
            "use_image": True,
            "image_generation_type": self.config.get("image_generation_type", "screenshot"),
            "screenshot_target": self.config.get("screenshot_target", "crypto-chart"),
            "crypto_news_enabled": self.config.get("crypto_news_enabled", True),
            "world_news_enabled": self.config.get("world_news_enabled", True),
            "use_image_flag": True,
            "dry_run": False,
            "use_openai_image_only": False,
        }
        if options:
            opts.update(options)

        logger.debug("Runner options: %s", json.dumps(opts, indent=2))
        news_items: List[Dict[str, str]] = []
        if opts["crypto_news_enabled"]:
            news_items.extend(self.fetch_crypto_news())
        if opts["world_news_enabled"]:
            news_items.extend(self.fetch_world_news())
        logger.debug("Total news items after fetch: %s", len(news_items))
        if not news_items:
            return {"success": False, "error": "No news items found"}

        headline, key_points = self.summarize_news(news_items)
        logger.debug("Headline after summary: %s", headline)
        logger.debug("Key points after summary: %s", key_points)
        tweet_text, format_used = self.build_tweet_text(headline, key_points)
        logger.debug("Tweet text (%s format): %s", format_used, tweet_text)

        media_path: Optional[str] = None
        if opts["use_image"]:
            # Check if OpenAI-only flag is set
            if opts.get("use_openai_image_only", False):
                logger.debug("useOpenAIImageOnly flag is true - using OpenAI image generation only")
                media_path = self.generate_ai_image(headline, key_points)
            else:
                gen_type = (opts.get("image_generation_type") or "ai").lower()
                logger.debug("Preparing media: type=%s", gen_type)
                if gen_type == "screenshot":
                    media_path = self.generate_screenshot(news_items, opts.get("screenshot_target", "crypto-chart"))
                elif gen_type == "both":
                    media_path = self.generate_ai_image(headline, key_points)
                    if not media_path:
                        media_path = self.generate_screenshot(
                            news_items, opts.get("screenshot_target", "crypto-chart")
                        )
                else:
                    media_path = self.generate_ai_image(headline, key_points)

        if opts.get("dry_run"):
            logger.info("Dry run complete; returning preview")
            if media_path:
                Path(media_path).unlink(missing_ok=True)
            return {
                "success": True,
                "dryRun": True,
                "tweetText": tweet_text,
                "format": format_used,
            }

        post_result = self.post_tweet(tweet_text, media_path)
        logger.info("Bot run complete; tweet id=%s", post_result.get("tweetId"))
        post_result.update({
            "headline": headline,
            "keyPoints": key_points,
            "format": format_used,
        })
        return post_result


# ----------------------------------------------------------------------
# FastAPI service for Railway deployment
# ----------------------------------------------------------------------

app = FastAPI(title="Twitter News Bot", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TwitterCredentials(BaseModel):
    twitter_api_key: Optional[str] = Field(None, alias="twitterApiKey")
    twitter_api_secret: Optional[str] = Field(None, alias="twitterApiSecret")
    twitter_access_token: Optional[str] = Field(None, alias="twitterAccessToken")
    twitter_access_secret: Optional[str] = Field(None, alias="twitterAccessSecret")
    openai_api_key: Optional[str] = Field(None, alias="openaiApiKey")
    news_api_key: Optional[str] = Field(None, alias="newsApiKey")
    uploadme_api_key: Optional[str] = Field(None, alias="uploadMeApiKey")


class RunRequest(BaseModel):
    credentials: Optional[TwitterCredentials] = None
    useImage: bool = True
    dryRun: bool = True
    imageGenerationType: str = "screenshot"
    screenshotTarget: str = "crypto-chart"
    useOpenAIImageOnly: bool = False  # If true, skip screenshots and use OpenAI only
    cryptoNewsEnabled: bool = True
    worldNewsEnabled: bool = True


class RunResponse(BaseModel):
    success: bool
    dryRun: Optional[bool] = None
    tweetText: Optional[str] = None
    tweetId: Optional[str] = None
    imageUrl: Optional[str] = None
    error: Optional[str] = None
    format: Optional[str] = None


def resolve_config(req: RunRequest) -> Dict[str, Any]:
    creds = req.credentials or TwitterCredentials()

    config = {
        "twitter_api_key": creds.twitter_api_key or os.getenv("TWITTER_API_KEY", ""),
        "twitter_api_secret": creds.twitter_api_secret or os.getenv("TWITTER_API_SECRET", ""),
        "twitter_access_token": creds.twitter_access_token or os.getenv("TWITTER_ACCESS_TOKEN", ""),
        "twitter_access_secret": creds.twitter_access_secret or os.getenv("TWITTER_ACCESS_SECRET", ""),
        "openai_api_key": creds.openai_api_key or os.getenv("OPENAI_API_KEY", ""),
        "news_api_key": creds.news_api_key or os.getenv("NEWS_API_KEY"),
        "uploadme_api_key": creds.uploadme_api_key or os.getenv("UPLOADME_API_KEY"),
        "crypto_news_enabled": req.cryptoNewsEnabled,
        "world_news_enabled": req.worldNewsEnabled,
        "image_generation_type": req.imageGenerationType,
        "screenshot_target": req.screenshotTarget,
    }

    missing = [key for key in [
        "twitter_api_key",
        "twitter_api_secret",
        "twitter_access_token",
        "twitter_access_secret",
        "openai_api_key",
    ] if not config[key]]

    if missing:
        raise HTTPException(status_code=400, detail=f"Missing credentials: {', '.join(missing)}")

    return config


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/run", response_model=RunResponse)
def trigger_run(req: RunRequest) -> RunResponse:
    config = resolve_config(req)
    bot = TwitterNewsBot(config)
    result = bot.run(
        {
            "use_image": req.useImage,
            "dry_run": req.dryRun,
            "image_generation_type": req.imageGenerationType,
            "screenshot_target": req.screenshotTarget,
            "use_openai_image_only": req.useOpenAIImageOnly,
            "crypto_news_enabled": req.cryptoNewsEnabled,
            "world_news_enabled": req.worldNewsEnabled,
        }
    )
    return RunResponse(**result)


def main() -> None:  # pragma: no cover - CLI helper
    import uvicorn

    uvicorn.run("bot:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))


if __name__ == "__main__":  # pragma: no cover
    main()

