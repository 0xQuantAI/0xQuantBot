import { TwitterApi } from 'twitter-api-v2';
import OpenAI from 'openai';
import axios from 'axios';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';
import { uploadToDropbox, validateDropboxConfig } from './dropbox-helper';

// Load environment variables from .env file
dotenv.config();

// Configuration
interface BotConfig {
  twitterApiKey: string;
  twitterApiSecret: string;
  twitterAccessToken: string;
  twitterAccessSecret: string;
  openaiApiKey: string;
  newsApiKey?: string;
  dropboxAccessToken?: string;
  cryptoNewsEnabled: boolean;
  worldNewsEnabled: boolean;
  postInterval: number; // minutes
}

interface NewsItem {
  title: string;
  description: string;
  url: string;
  publishedAt: string;
  source: string;
}

class TwitterNewsBot {
  private twitterClient: TwitterApi;
  private openai: OpenAI;
  private config: BotConfig;

  constructor(config: BotConfig) {
    this.config = config;
    
    // Initialize Twitter client
    this.twitterClient = new TwitterApi({
      appKey: config.twitterApiKey,
      appSecret: config.twitterApiSecret,
      accessToken: config.twitterAccessToken,
      accessSecret: config.twitterAccessSecret,
    });

    // Initialize OpenAI
    this.openai = new OpenAI({
      apiKey: config.openaiApiKey,
    });
  }

  /**
   * Fetch crypto news from CryptoPanic API (free alternative)
   */
  async fetchCryptoNews(): Promise<NewsItem[]> {
    try {
      const response = await axios.get('https://cryptopanic.com/api/v1/posts/', {
        params: {
          auth_token: 'free', // Use 'free' or register for API key
          kind: 'news',
          filter: 'important'
        }
      });

      return response.data.results.slice(0, 5).map((item: any) => ({
        title: item.title,
        description: item.title,
        url: item.url,
        publishedAt: item.published_at,
        source: item.source.title
      }));
    } catch (error) {
      console.error('Error fetching crypto news:', error);
      
      // Fallback to CoinGecko trending
      try {
        const response = await axios.get('https://api.coingecko.com/api/v3/search/trending');
        return response.data.coins.slice(0, 5).map((item: any) => ({
          title: `${item.item.name} (${item.item.symbol}) is trending`,
          description: `Market Cap Rank: #${item.item.market_cap_rank}`,
          url: `https://www.coingecko.com/en/coins/${item.item.id}`,
          publishedAt: new Date().toISOString(),
          source: 'CoinGecko'
        }));
      } catch (fallbackError) {
        console.error('Fallback crypto news failed:', fallbackError);
        return [];
      }
    }
  }

  /**
   * Fetch world news using NewsAPI
   */
  async fetchWorldNews(): Promise<NewsItem[]> {
    try {
      // Using NewsAPI.org (requires free API key)
      // Alternative: Use RSS feeds or other free sources
      const response = await axios.get('https://newsapi.org/v2/top-headlines', {
        params: {
          apiKey: this.config.newsApiKey || 'demo',
          category: 'technology',
          language: 'en',
          pageSize: 5
        }
      });

      return response.data.articles.map((article: any) => ({
        title: article.title,
        description: article.description || article.title,
        url: article.url,
        publishedAt: article.publishedAt,
        source: article.source.name
      }));
    } catch (error) {
      console.error('Error fetching world news:', error);
      
      // Fallback to HackerNews
      try {
        const topStories = await axios.get('https://hacker-news.firebaseio.com/v0/topstories.json');
        const stories = await Promise.all(
          topStories.data.slice(0, 5).map(async (id: number) => {
            const story = await axios.get(`https://hacker-news.firebaseio.com/v0/item/${id}.json`);
            return story.data;
          })
        );

        return stories.map((story: any) => ({
          title: story.title,
          description: story.title,
          url: story.url || `https://news.ycombinator.com/item?id=${story.id}`,
          publishedAt: new Date(story.time * 1000).toISOString(),
          source: 'HackerNews'
        }));
      } catch (fallbackError) {
        console.error('Fallback world news failed:', fallbackError);
        return [];
      }
    }
  }

  /**
   * Summarize news using OpenAI
   */
  async summarizeNews(newsItems: NewsItem[]): Promise<string> {
    const newsText = newsItems.map((item, index) => 
      `${index + 1}. ${item.title}\nSource: ${item.source}\n`
    ).join('\n');

    const prompt = `Analyze these news items and create a concise, engaging summary in 2-3 sentences. Focus on key insights and trends. Make it suitable for a Twitter post (under 280 characters):

${newsText}

Summary:`;

    try {
      const response = await this.openai.chat.completions.create({
        model: 'gpt-4o-mini',
        messages: [
          {
            role: 'system',
            content: 'You are a professional news analyst who creates concise, engaging summaries for social media. Keep responses under 250 characters.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        max_tokens: 150,
        temperature: 0.7,
      });

      return response.choices[0]?.message?.content || 'Unable to generate summary';
    } catch (error) {
      console.error('Error summarizing news:', error);
      return newsItems[0]?.title || 'Latest news update';
    }
  }

  /**
   * Generate image using OpenAI Image generation
   */
  async generateImage(prompt: string): Promise<string | null> {
    try {
      const response = await this.openai.images.generate({
        model: 'dall-e-3',
        prompt: `Create a professional, modern graphic for a news post about: ${prompt}. Style: clean, tech-focused, suitable for Twitter.`,
        n: 1,
        size: '1024x1024',
        quality: 'standard',
      });

      const imageUrl = response.data?.[0]?.url;
      if (!imageUrl) return null;

      // Download image
      const imageResponse = await axios.get(imageUrl, { responseType: 'arraybuffer' });
      const imagePath = path.join(__dirname, 'temp', `news_${Date.now()}.png`);
      
      // Ensure temp directory exists
      if (!fs.existsSync(path.join(__dirname, 'temp'))) {
        fs.mkdirSync(path.join(__dirname, 'temp'), { recursive: true });
      }

      fs.writeFileSync(imagePath, imageResponse.data);
      return imagePath;
    } catch (error) {
      console.error('Error generating image:', error);
      return null;
    }
  }

  /**
   * Generate video using Sora (placeholder - Sora API not publicly available yet)
   */
  async generateVideo(prompt: string): Promise<string | null> {
    console.log('Video generation requested for:', prompt);
    console.log('Note: Sora API is not yet publicly available. This is a placeholder.');
    
    // When Sora becomes available, implement like this:
    /*
    try {
      const response = await this.openai.videos.generate({
        model: 'sora-1.0',
        prompt: `Create a short video about: ${prompt}`,
        duration: 5,
      });
      
      const videoUrl = response.data[0]?.url;
      if (!videoUrl) return null;

      // Download video
      const videoResponse = await axios.get(videoUrl, { responseType: 'arraybuffer' });
      const videoPath = path.join(__dirname, 'temp', `news_${Date.now()}.mp4`);
      fs.writeFileSync(videoPath, videoResponse.data);
      return videoPath;
    } catch (error) {
      console.error('Error generating video:', error);
      return null;
    }
    */
    
    return null;
  }

  /**
   * Post tweet with optional media
   */
  async postTweet(text: string, mediaPath?: string): Promise<void> {
    try {
      const client = this.twitterClient.v2;
      let finalTweetText = text;

      if (mediaPath && fs.existsSync(mediaPath)) {
        // Try direct upload first (works with Elevated/Basic tier)
        try {
          const mediaId = await this.twitterClient.v1.uploadMedia(mediaPath);
          
          // Post tweet with media
          const tweet = await client.tweet({
            text,
            media: { media_ids: [mediaId] }
          });

          console.log('✓ Tweet posted successfully with direct media upload!');
          console.log(`  Tweet ID: ${tweet.data.id}`);
          console.log(`  Tweet text: ${text}`);

          // Clean up temp file
          fs.unlinkSync(mediaPath);
          return;
        } catch (uploadError: any) {
          // If upload fails with 403, try Dropbox fallback
          if (uploadError.code === 403 && this.config.dropboxAccessToken && validateDropboxConfig(this.config.dropboxAccessToken)) {
            console.log('   ⚠ Direct media upload failed (Free tier limitation)');
            console.log('   → Using Dropbox fallback...');
            
            const dropboxUrl = await uploadToDropbox(mediaPath, this.config.dropboxAccessToken);
            
            if (dropboxUrl) {
              // Add image URL to tweet text (X will show preview automatically)
              const maxTextLength = 280 - dropboxUrl.length - 2; // -2 for newline
              if (text.length > maxTextLength) {
                finalTweetText = text.substring(0, maxTextLength - 3) + '...';
              }
              finalTweetText = `${finalTweetText}\n${dropboxUrl}`;
              
              // Clean up temp file
              fs.unlinkSync(mediaPath);
            } else {
              console.log('   ⚠ Dropbox upload also failed, posting text-only');
              // Clean up temp file
              fs.unlinkSync(mediaPath);
            }
          } else {
            // No Dropbox configured or other error, post text-only
            console.log('   ⚠ Media upload failed, posting text-only');
            console.log('   → Configure DROPBOX_ACCESS_TOKEN in .env to enable image fallback');
            if (fs.existsSync(mediaPath)) {
              fs.unlinkSync(mediaPath);
            }
          }
        }
      }

      // Post text-only tweet or tweet with Dropbox URL
      const tweet = await client.tweet({ text: finalTweetText });
      
      console.log('✓ Tweet posted successfully!');
      console.log(`  Tweet ID: ${tweet.data.id}`);
      console.log(`  Tweet text: ${finalTweetText}`);
    } catch (error) {
      console.error('Error posting tweet:', error);
      throw error;
    }
  }

  /**
   * Main bot workflow
   */
  async run(options: { useImage?: boolean; useVideo?: boolean } = {}): Promise<void> {
    try {
      console.log('🤖 Starting Twitter News Bot...');
      console.log('⏰', new Date().toLocaleString());
      console.log('');

      // Fetch news
      console.log('📰 Fetching news...');
      let newsItems: NewsItem[] = [];

      if (this.config.cryptoNewsEnabled) {
        const cryptoNews = await this.fetchCryptoNews();
        newsItems.push(...cryptoNews);
        console.log(`   ✓ Fetched ${cryptoNews.length} crypto news items`);
      }

      if (this.config.worldNewsEnabled) {
        const worldNews = await this.fetchWorldNews();
        newsItems.push(...worldNews);
        console.log(`   ✓ Fetched ${worldNews.length} world news items`);
      }

      if (newsItems.length === 0) {
        console.log('   ✗ No news items found');
        return;
      }

      // Summarize news
      console.log('');
      console.log('💡 Generating summary with AI...');
      const summary = await this.summarizeNews(newsItems);
      console.log(`   ✓ Summary: "${summary}"`);

      // Generate media
      let mediaPath: string | null = null;

      if (options.useVideo) {
        console.log('');
        console.log('🎬 Generating video...');
        mediaPath = await this.generateVideo(summary);
        if (mediaPath) {
          console.log(`   ✓ Video generated: ${mediaPath}`);
        } else {
          console.log('   ⚠ Video generation not available, falling back to image');
          options.useImage = true;
        }
      }

      if (options.useImage && !mediaPath) {
        console.log('');
        console.log('🎨 Generating image with OpenAI Image generation...');
        mediaPath = await this.generateImage(summary);
        if (mediaPath) {
          console.log(`   ✓ Image generated: ${mediaPath}`);
        } else {
          console.log('   ⚠ Image generation failed');
        }
      }

      // Add hashtags and source
      const topSource = newsItems[0]?.source || 'News';
      const tweetText = `${summary}\n\n#Crypto #AI #News\n\nSource: ${topSource}`;

      // Ensure tweet is under 280 characters
      const finalTweet = tweetText.length > 280 
        ? summary + '\n\n#Crypto #News' 
        : tweetText;

      // Post tweet
      console.log('');
      console.log('🐦 Posting to Twitter...');
      await this.postTweet(finalTweet, mediaPath || undefined);

      console.log('');
      console.log('✅ Bot run completed successfully!');
      console.log('═'.repeat(50));
    } catch (error) {
      console.error('❌ Error in bot run:', error);
      throw error;
    }
  }

  /**
   * Start bot with scheduled posts
   */
  startScheduled(options: { useImage?: boolean; useVideo?: boolean } = {}): void {
    console.log('🚀 Starting scheduled Twitter News Bot');
    console.log(`⏱  Posting every ${this.config.postInterval} minutes`);
    console.log('═'.repeat(50));

    // Run immediately
    this.run(options);

    // Then run on schedule
    setInterval(() => {
      this.run(options);
    }, this.config.postInterval * 60 * 1000);
  }
}

// Export the bot class
export default TwitterNewsBot;

// CLI execution
if (require.main === module) {
  // Load configuration from environment variables
  const config: BotConfig = {
    twitterApiKey: process.env.TWITTER_API_KEY || '',
    twitterApiSecret: process.env.TWITTER_API_SECRET || '',
    twitterAccessToken: process.env.TWITTER_ACCESS_TOKEN || '',
    twitterAccessSecret: process.env.TWITTER_ACCESS_SECRET || '',
    openaiApiKey: process.env.OPENAI_API_KEY || '',
    newsApiKey: process.env.NEWS_API_KEY,
    dropboxAccessToken: process.env.DROPBOX_ACCESS_TOKEN,
    cryptoNewsEnabled: true,
    worldNewsEnabled: true,
    postInterval: 60, // 60 minutes
  };

  // Validate configuration
  if (!config.twitterApiKey || !config.twitterApiSecret || 
      !config.twitterAccessToken || !config.twitterAccessSecret) {
    console.error('❌ Error: Twitter API credentials not configured');
    console.error('Please set the following environment variables:');
    console.error('  - TWITTER_API_KEY');
    console.error('  - TWITTER_API_SECRET');
    console.error('  - TWITTER_ACCESS_TOKEN');
    console.error('  - TWITTER_ACCESS_SECRET');
    process.exit(1);
  }

  if (!config.openaiApiKey) {
    console.error('❌ Error: OpenAI API key not configured');
    console.error('Please set OPENAI_API_KEY environment variable');
    process.exit(1);
  }

  // Parse command line arguments
  const args = process.argv.slice(2);
  const useImage = args.includes('--image') || args.includes('-i');
  const useVideo = args.includes('--video') || args.includes('-v');
  const scheduled = args.includes('--scheduled') || args.includes('-s');
  const once = args.includes('--once') || args.includes('-o');

  // Create and run bot
  const bot = new TwitterNewsBot(config);

  if (scheduled) {
    bot.startScheduled({ useImage, useVideo });
  } else {
    bot.run({ useImage, useVideo }).catch(error => {
      console.error('Fatal error:', error);
      process.exit(1);
    });
  }
}

