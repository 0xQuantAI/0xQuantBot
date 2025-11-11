import { TwitterApi } from 'twitter-api-v2';
import OpenAI from 'openai';
import axios from 'axios';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Import the bot
import TwitterNewsBot from './bot';

// Configuration
const config = {
  twitterApiKey: process.env.TWITTER_API_KEY || '',
  twitterApiSecret: process.env.TWITTER_API_SECRET || '',
  twitterAccessToken: process.env.TWITTER_ACCESS_TOKEN || '',
  twitterAccessSecret: process.env.TWITTER_ACCESS_SECRET || '',
  openaiApiKey: process.env.OPENAI_API_KEY || '',
  newsApiKey: process.env.NEWS_API_KEY,
  cryptoNewsEnabled: true,
  worldNewsEnabled: true,
  postInterval: 60,
};

// Test mode: Fetch news and generate summary without posting
async function testBot() {
  console.log('🧪 Twitter Bot - TEST MODE');
  console.log('═'.repeat(50));
  console.log('This will fetch news and generate a summary WITHOUT posting to Twitter');
  console.log('');

  const bot = new TwitterNewsBot(config);
  
  try {
    console.log('📰 Fetching news...');
    
    // Fetch crypto news
    const cryptoNews = await (bot as any).fetchCryptoNews();
    console.log(`   ✓ Fetched ${cryptoNews.length} crypto news items`);
    
    // Fetch world news
    const worldNews = await (bot as any).fetchWorldNews();
    console.log(`   ✓ Fetched ${worldNews.length} world news items`);
    
    const allNews = [...cryptoNews, ...worldNews];
    
    if (allNews.length === 0) {
      console.log('   ✗ No news found');
      return;
    }
    
    // Show fetched news
    console.log('');
    console.log('📋 News Items:');
    allNews.forEach((item, i) => {
      console.log(`   ${i + 1}. ${item.title}`);
      console.log(`      Source: ${item.source}`);
    });
    
    // Generate summary
    console.log('');
    console.log('💡 Generating AI summary...');
    const summary = await (bot as any).summarizeNews(allNews);
    console.log(`   ✓ Summary generated`);
    
    // Create tweet text
    const topSource = allNews[0]?.source || 'News';
    const tweetText = `${summary}\n\n#Crypto #AI #News\n\nSource: ${topSource}`;
    const finalTweet = tweetText.length > 280 ? summary + '\n\n#Crypto #News' : tweetText;
    
    // Show what would be posted
    console.log('');
    console.log('═'.repeat(50));
    console.log('📝 Generated Tweet (would be posted):');
    console.log('═'.repeat(50));
    console.log(finalTweet);
    console.log('═'.repeat(50));
    console.log(`Length: ${finalTweet.length}/280 characters`);
    console.log('');
    console.log('✅ Test completed successfully!');
    console.log('');
    console.log('To enable actual posting:');
    console.log('1. Go to https://developer.twitter.com/en/portal/dashboard');
    console.log('2. Select your app');
    console.log('3. Go to "Settings" → "User authentication settings"');
    console.log('4. Ensure "Read and Write" permissions are enabled');
    console.log('5. Regenerate your Access Token and Secret');
    console.log('6. Update your .env file with new tokens');
    console.log('7. Run: npm run once');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
}

// Run test
testBot();

