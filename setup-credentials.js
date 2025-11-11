#!/usr/bin/env node
/**
 * Setup script to copy credentials from main .env to bot .env
 * Run this from the twitter-bot directory
 */

const fs = require('fs');
const path = require('path');

console.log('🔧 Twitter Bot Credentials Setup');
console.log('═'.repeat(50));

// Path to main project .env
const mainEnvPath = path.join(__dirname, '..', '.env');
const botEnvPath = path.join(__dirname, '.env');
const exampleEnvPath = path.join(__dirname, '.env.example');

// Check if main .env exists
if (!fs.existsSync(mainEnvPath)) {
  console.error('❌ Main project .env file not found');
  console.log('Please create .env in the project root first');
  process.exit(1);
}

// Read main .env
console.log('📖 Reading main project .env...');
const mainEnv = fs.readFileSync(mainEnvPath, 'utf8');

// Parse environment variables
const envVars = {};
mainEnv.split('\n').forEach(line => {
  const trimmed = line.trim();
  if (trimmed && !trimmed.startsWith('#')) {
    const [key, ...valueParts] = trimmed.split('=');
    const value = valueParts.join('=');
    if (key && value) {
      envVars[key.trim()] = value.trim();
    }
  }
});

// Map credentials
const credentials = {
  TWITTER_API_KEY: envVars.API_KEY || envVars.TWITTER_API_KEY || '',
  TWITTER_API_SECRET: envVars.API_SECRET || envVars.TWITTER_API_SECRET || '',
  TWITTER_ACCESS_TOKEN: envVars.ACCESS_TOKEN || envVars.TWITTER_ACCESS_TOKEN || '',
  TWITTER_ACCESS_SECRET: envVars.ACCESS_SECRET || envVars.TWITTER_ACCESS_SECRET || '',
  OPENAI_API_KEY: envVars.OPENAI_API_KEY || '',
  NEWS_API_KEY: envVars.NEWS_API_KEY || '',
  POST_INTERVAL: '60',
  CRYPTO_NEWS_ENABLED: 'true',
  WORLD_NEWS_ENABLED: 'true'
};

// Check if essential credentials exist
const missingCredentials = [];
if (!credentials.TWITTER_API_KEY) missingCredentials.push('TWITTER_API_KEY (or API_KEY)');
if (!credentials.TWITTER_API_SECRET) missingCredentials.push('TWITTER_API_SECRET (or API_SECRET)');
if (!credentials.TWITTER_ACCESS_TOKEN) missingCredentials.push('TWITTER_ACCESS_TOKEN (or ACCESS_TOKEN)');
if (!credentials.TWITTER_ACCESS_SECRET) missingCredentials.push('TWITTER_ACCESS_SECRET (or ACCESS_SECRET)');
if (!credentials.OPENAI_API_KEY) missingCredentials.push('OPENAI_API_KEY');

if (missingCredentials.length > 0) {
  console.warn('⚠ Warning: Missing credentials in main .env:');
  missingCredentials.forEach(cred => console.log(`  - ${cred}`));
  console.log('');
  console.log('Please add these to your main project .env file first');
  console.log('Or manually edit twitter-bot/.env after this script completes');
  console.log('');
}

// Create bot .env content
const botEnvContent = `# Twitter API Credentials
TWITTER_API_KEY=${credentials.TWITTER_API_KEY}
TWITTER_API_SECRET=${credentials.TWITTER_API_SECRET}
TWITTER_ACCESS_TOKEN=${credentials.TWITTER_ACCESS_TOKEN}
TWITTER_ACCESS_SECRET=${credentials.TWITTER_ACCESS_SECRET}

# OpenAI API Key
OPENAI_API_KEY=${credentials.OPENAI_API_KEY}

# NewsAPI Key (Optional)
NEWS_API_KEY=${credentials.NEWS_API_KEY}

# Bot Configuration
POST_INTERVAL=${credentials.POST_INTERVAL}
CRYPTO_NEWS_ENABLED=${credentials.CRYPTO_NEWS_ENABLED}
WORLD_NEWS_ENABLED=${credentials.WORLD_NEWS_ENABLED}
`;

// Write bot .env
console.log('✍️  Writing twitter-bot/.env...');
fs.writeFileSync(botEnvPath, botEnvContent);

console.log('✅ Credentials copied successfully!');
console.log('');
console.log('Configuration:');
console.log('  Twitter API Key:', credentials.TWITTER_API_KEY ? '✓ Set' : '✗ Missing');
console.log('  Twitter API Secret:', credentials.TWITTER_API_SECRET ? '✓ Set' : '✗ Missing');
console.log('  Twitter Access Token:', credentials.TWITTER_ACCESS_TOKEN ? '✓ Set' : '✗ Missing');
console.log('  Twitter Access Secret:', credentials.TWITTER_ACCESS_SECRET ? '✓ Set' : '✗ Missing');
console.log('  OpenAI API Key:', credentials.OPENAI_API_KEY ? '✓ Set' : '✗ Missing');
console.log('  NewsAPI Key:', credentials.NEWS_API_KEY ? '✓ Set' : '(Optional)');
console.log('');

if (missingCredentials.length === 0) {
  console.log('🎉 All credentials configured!');
  console.log('');
  console.log('Next steps:');
  console.log('  1. Install dependencies: npm install');
  console.log('  2. Test the bot: npm run once');
  console.log('  3. Run with images: npm run once:image');
  console.log('  4. Schedule posts: npm run scheduled:image');
} else {
  console.log('⚠️  Please configure missing credentials before running the bot');
  console.log('   Edit twitter-bot/.env or the main project .env');
}

console.log('');
console.log('═'.repeat(50));

