# Quick Start Guide 🚀

Get your Twitter News Bot running in 5 minutes!

## Step 1: Get Your Credentials 🔑

### Twitter API (Required)
1. Go to https://developer.twitter.com/en/portal/dashboard
2. Create a new app or select existing one
3. Go to "Keys and tokens" tab
4. Copy these 4 values:
   - API Key
   - API Secret
   - Access Token
   - Access Secret

### OpenAI API (Required)
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (you won't see it again!)

### NewsAPI (Optional)
1. Go to https://newsapi.org/register
2. Sign up for free tier
3. Copy your API key

## Step 2: Install Dependencies 📦

### Option A: TypeScript/Node.js (Recommended if you're already using Node.js)

```bash
cd twitter-bot
npm install
```

### Option B: Python

```bash
cd twitter-bot
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 3: Configure Environment 🔧

```bash
# Copy the example file
cp .env.example .env

# Edit with your credentials
nano .env  # or use any text editor
```

Paste your credentials:
```env
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_SECRET=your_access_secret_here
OPENAI_API_KEY=sk-...your_key_here
NEWS_API_KEY=your_news_api_key_here
```

## Step 4: Test Run 🧪

### TypeScript
```bash
npm run once
```

### Python
```bash
python bot.py --once
```

You should see:
```
🤖 Starting Twitter News Bot...
⏰ 2025-01-10 10:30:00

📰 Fetching news...
   ✓ Fetched 5 crypto news items
   ✓ Fetched 5 world news items

💡 Generating summary with AI...
   ✓ Summary: "Bitcoin hits new ATH as institutions..."

🐦 Posting to Twitter...
✓ Tweet posted successfully!
  Tweet ID: 1234567890
  Tweet text: Bitcoin hits new ATH...

✅ Bot run completed successfully!
```

## Step 5: Run with Images 🎨

### TypeScript
```bash
npm run once:image
```

### Python
```bash
python bot.py --once --image
```

## Step 6: Schedule Automated Posts ⏰

### TypeScript
```bash
npm run scheduled:image
```

### Python
```bash
python bot.py --scheduled --image
```

This will post every 60 minutes (configurable in .env).

## Verify Your Bot is Working ✅

1. Check your Twitter feed
2. Look for the new post
3. Verify it has the summary and image (if enabled)

## Troubleshooting 🔍

### "Error: Unauthorized"
- Double-check your Twitter API credentials
- Ensure your app has "Read and Write" permissions
- Try regenerating your access tokens

### "Error: Invalid OpenAI API key"
- Verify you copied the entire key (starts with 'sk-')
- Check if you have credits in your OpenAI account
- Make sure the key hasn't expired

### "No news items found"
- Check your internet connection
- The bot uses fallback sources automatically
- Try running again in a few minutes

### "Image generation failed"
- Requires OpenAI credits (~$0.04 per image)
- Check your OpenAI billing
- Bot will post text-only if image fails

## Next Steps 🎯

1. **Customize**: Edit tweet format in `bot.ts` or `bot.py`
2. **Schedule**: Adjust `POST_INTERVAL` in `.env`
3. **Deploy**: See Production Deployment in README.md
4. **Monitor**: Check Twitter and API usage regularly

## Quick Commands Reference 📝

### TypeScript
```bash
npm run once          # Post once, text only
npm run once:image    # Post once with image
npm run scheduled     # Auto-post every interval
```

### Python
```bash
python bot.py --once            # Post once
python bot.py --once --image    # Post once with image
python bot.py --scheduled       # Auto-post every interval
```

## Pro Tips 💡

1. **Start with text-only** to save costs while testing
2. **Use --once flag** for initial testing
3. **Monitor your costs** in OpenAI dashboard
4. **Post every 2-4 hours** for better engagement
5. **Customize hashtags** for your audience

## Need Help? 🆘

- Read the full README.md for detailed documentation
- Check Twitter API docs: https://developer.twitter.com/docs
- Check OpenAI docs: https://platform.openai.com/docs

---

**You're all set! Happy tweeting! 🐦✨**

