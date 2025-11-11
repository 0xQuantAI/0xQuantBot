# Twitter News Bot 🤖🐦

An automated Twitter bot that fetches the latest crypto and world news, summarizes them with AI, generates images/videos, and posts to Twitter.

## Features ✨

- **News Fetching**: Automatically fetches latest crypto and world news from multiple sources
- **AI Summarization**: Uses OpenAI GPT-4 to create concise, engaging summaries
- **Image Generation**: Creates custom images with DALL-E 3
- **Video Generation**: Placeholder for Sora video generation (when available)
- **Automated Posting**: Posts to Twitter on a schedule or on-demand
- **Multiple Sources**: CryptoPanic, CoinGecko, NewsAPI, HackerNews
- **Dual Implementation**: Available in both TypeScript and Python

## Prerequisites 📋

### Twitter API Access
1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new app (or use existing one)
3. Get your credentials:
   - API Key
   - API Secret
   - Access Token
   - Access Secret

### OpenAI API Access
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an API key
3. Note: Image generation requires credits

### Optional: NewsAPI Access
1. Go to [NewsAPI](https://newsapi.org/register)
2. Get a free API key for world news (optional - will use HackerNews as fallback)

## Installation 🚀

### TypeScript/Node.js Version

```bash
cd twitter-bot

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### Python Version

```bash
cd twitter-bot

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

## Configuration ⚙️

Edit the `.env` file with your credentials:

```env
# Required
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_SECRET=your_access_secret_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional
NEWS_API_KEY=your_news_api_key_here
POST_INTERVAL=60
```

## Usage 🎯

### TypeScript/Node.js

```bash
# Run once (text only)
npm run once

# Run once with image
npm run once:image

# Run once with video (placeholder)
npm run once:video

# Run on schedule (every 60 minutes, text only)
npm run scheduled

# Run on schedule with images
npm run scheduled:image

# Direct execution with options
ts-node bot.ts --once --image
ts-node bot.ts --scheduled --image
```

### Python

```bash
# Run once (text only)
python bot.py --once

# Run once with image
python bot.py --once --image

# Run once with video (placeholder)
python bot.py --once --video

# Run on schedule (every 60 minutes)
python bot.py --scheduled

# Run on schedule with images
python bot.py --scheduled --image
```

## Command Line Options 🎛️

| Option | Short | Description |
|--------|-------|-------------|
| `--once` | `-o` | Run once and exit |
| `--scheduled` | `-s` | Run on schedule (interval in .env) |
| `--image` | `-i` | Generate and attach image |
| `--video` | `-v` | Generate and attach video (Sora placeholder) |

## How It Works 🔧

1. **Fetch News**: Retrieves latest news from multiple sources
   - Crypto: CryptoPanic API → CoinGecko (fallback)
   - World: NewsAPI → HackerNews (fallback)

2. **Summarize**: Uses OpenAI GPT-4 Mini to create a concise summary
   - Analyzes all fetched news items
   - Creates engaging 2-3 sentence summary
   - Optimized for Twitter (under 280 characters)

3. **Generate Media** (optional):
   - **Images**: DALL-E 3 creates custom graphics
   - **Videos**: Placeholder for Sora (not yet available)

4. **Post to Twitter**: Publishes tweet with summary and media
   - Includes hashtags (#Crypto #AI #News)
   - Adds source attribution
   - Automatic character limit handling

## News Sources 📰

### Crypto News
- **Primary**: [CryptoPanic](https://cryptopanic.com) - Real-time crypto news aggregator
- **Fallback**: [CoinGecko](https://www.coingecko.com) - Trending cryptocurrencies

### World News
- **Primary**: [NewsAPI](https://newsapi.org) - Technology news headlines
- **Fallback**: [HackerNews](https://news.ycombinator.com) - Tech community news

## Project Structure 📁

```
twitter-bot/
├── bot.ts              # TypeScript implementation
├── bot.py              # Python implementation
├── package.json        # Node.js dependencies & scripts
├── requirements.txt    # Python dependencies
├── tsconfig.json       # TypeScript configuration
├── .env.example        # Environment variables template
├── .env                # Your credentials (create this)
├── temp/               # Temporary directory for generated media
└── README.md           # This file
```

## Cost Considerations 💰

### OpenAI API Costs (Approximate)
- **GPT-4o-mini** (Summarization): ~$0.0001 per run
- **DALL-E 3** (Image Generation): ~$0.04 per image
- **Sora** (Video Generation): TBA (not yet available)

**Estimated Monthly Cost** (posting every hour with images):
- ~720 posts/month × $0.0401 = ~$28.87/month

**Cost Saving Tips**:
- Post less frequently (every 2-4 hours)
- Use text-only mode (no images)
- Use GPT-3.5-turbo instead of GPT-4

## Troubleshooting 🔍

### Common Issues

1. **Twitter API Errors**
   ```
   Error: Unauthorized
   ```
   - Verify your API credentials
   - Ensure your Twitter app has Read & Write permissions
   - Regenerate access tokens if needed

2. **OpenAI Rate Limits**
   ```
   Error: Rate limit exceeded
   ```
   - Reduce posting frequency
   - Check your OpenAI usage limits
   - Consider upgrading your OpenAI plan

3. **News Fetching Fails**
   ```
   No news items found
   ```
   - Check your internet connection
   - Verify NewsAPI key (if using)
   - Fallback sources should activate automatically

4. **Image Generation Fails**
   ```
   Image generation failed
   ```
   - Ensure sufficient OpenAI credits
   - Check prompt content (no policy violations)
   - Bot will post text-only if image fails

## Customization 🎨

### Modify News Categories

**TypeScript** (`bot.ts`):
```typescript
const config: BotConfig = {
  // ... other config
  cryptoNewsEnabled: true,  // Toggle crypto news
  worldNewsEnabled: false,  // Toggle world news
};
```

**Python** (`bot.py`):
```python
config = {
    # ... other config
    'crypto_news_enabled': True,  # Toggle crypto news
    'world_news_enabled': False,  # Toggle world news
}
```

### Change Posting Frequency

In `.env`:
```env
POST_INTERVAL=120  # Post every 120 minutes (2 hours)
```

### Customize Tweet Format

Edit the tweet text generation in `bot.ts` or `bot.py`:

```typescript
// TypeScript
const tweetText = `${summary}\n\n#YourHashtags\n\nSource: ${topSource}`;
```

```python
# Python
tweet_text = f"{summary}\n\n#YourHashtags\n\nSource: {top_source}"
```

## Production Deployment 🚀

### Using PM2 (Node.js)

```bash
# Install PM2
npm install -g pm2

# Start bot
pm2 start npm --name "twitter-bot" -- run scheduled:image

# Monitor
pm2 logs twitter-bot
pm2 status

# Auto-restart on system reboot
pm2 startup
pm2 save
```

### Using systemd (Linux)

Create `/etc/systemd/system/twitter-bot.service`:

```ini
[Unit]
Description=Twitter News Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/twitter-bot
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm run scheduled:image
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable twitter-bot
sudo systemctl start twitter-bot
sudo systemctl status twitter-bot
```

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

CMD ["npm", "run", "scheduled:image"]
```

Build and run:
```bash
docker build -t twitter-bot .
docker run -d --env-file .env --name twitter-bot twitter-bot
```

## Security Best Practices 🔒

1. **Never commit `.env` file** - Already in `.gitignore`
2. **Use environment variables** - Don't hardcode credentials
3. **Rotate API keys regularly** - Every 3-6 months
4. **Monitor API usage** - Check for unusual activity
5. **Limit token permissions** - Only grant necessary Twitter permissions

## Future Enhancements 🚧

- [ ] Sora video generation integration (when API available)
- [ ] Multiple news categories support
- [ ] Sentiment analysis for news filtering
- [ ] Thread posting for longer summaries
- [ ] Reply to comments with AI
- [ ] Analytics tracking (likes, retweets, impressions)
- [ ] Web dashboard for monitoring
- [ ] Multiple social media platforms (LinkedIn, Facebook)

## Contributing 🤝

Feel free to submit issues and enhancement requests!

## License 📄

MIT License - Feel free to use and modify for your projects.

## Support 💬

For issues or questions:
1. Check the troubleshooting section
2. Review Twitter API documentation
3. Check OpenAI API status
4. Create an issue with detailed error logs

## Disclaimer ⚠️

This bot is for educational and personal use. Ensure compliance with:
- Twitter's Automation Rules
- OpenAI's Usage Policies
- News source Terms of Service
- Applicable laws and regulations

**Important**: 
- Don't spam or abuse the bot
- Respect API rate limits
- Monitor costs carefully
- Follow platform guidelines

## Acknowledgments 🙏

- [twitter-api-v2](https://github.com/PLhery/node-twitter-api-v2) - Twitter API library
- [OpenAI](https://openai.com) - AI models
- [Tweepy](https://www.tweepy.org/) - Python Twitter library
- [CryptoPanic](https://cryptopanic.com) - Crypto news API
- [NewsAPI](https://newsapi.org) - World news API

---

**Made with ❤️ for the crypto community**

Happy Tweeting! 🐦✨

