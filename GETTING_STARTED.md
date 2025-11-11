# Getting Started with Your Twitter News Bot 🚀

## What You've Got 🎁

Your new Twitter bot can:
- ✅ Fetch latest crypto news (CryptoPanic, CoinGecko)
- ✅ Fetch world tech news (NewsAPI, HackerNews)
- ✅ Summarize news with AI (OpenAI GPT-4)
- ✅ Generate images with DALL-E 3
- ✅ Post to Twitter automatically
- ✅ Run on schedule or on-demand
- ✅ Available in TypeScript AND Python

## Your Credentials ✅

You already have these in your main `.env`:
```
API_KEY=bKMcxg9UAiIfSMkVbJ5rUo3cx
API_SECRET=L1oTVjlsagnHXowW2mNe0iyoigkOIeObjBvk7nmrSQ78Tm1Ewh
ACCESS_TOKEN=1516993682137825280-jQFECYSdPYr0tHwXkd1mJv8XRHhyZS
ACCESS_SECRET=fBgJbsHfS43XwRanFFzvntmOs66nVYAYT6rYH1f7Qhobb
OPENAI_API_KEY=sk-proj-...
```

## Quick Setup (2 minutes) ⚡

### Step 1: Navigate to the bot directory
```bash
cd twitter-bot
```

### Step 2: Copy credentials automatically
```bash
node setup-credentials.js
```

This will copy your Twitter and OpenAI credentials from the main `.env` to the bot's `.env`.

### Step 3: Install dependencies

**Option A - TypeScript (Recommended):**
```bash
npm install
```

**Option B - Python:**
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 4: Run your first tweet! 🎉

**TypeScript:**
```bash
npm run once
```

**Python:**
```bash
python bot.py --once
```

## What Happens When You Run It? 🔄

1. **Fetches News** (5 crypto + 5 world news items)
2. **Summarizes with AI** (creates engaging 2-3 sentence summary)
3. **Posts to Twitter** (with hashtags and source)

Example output:
```
🤖 Starting Twitter News Bot...
⏰ 2025-10-11 10:30:00

📰 Fetching news...
   ✓ Fetched 5 crypto news items
   ✓ Fetched 5 world news items

💡 Generating summary with AI...
   ✓ Summary: "Bitcoin reaches new milestone as institutional..."

🐦 Posting to Twitter...
✓ Tweet posted successfully!
  Tweet ID: 1234567890

✅ Bot run completed successfully!
```

## Run with Images 🎨

Add AI-generated images to your tweets:

**TypeScript:**
```bash
npm run once:image
```

**Python:**
```bash
python bot.py --once --image
```

**Note:** This costs ~$0.04 per image from OpenAI.

## Automate It! ⏰

Run every hour automatically:

**TypeScript:**
```bash
npm run scheduled:image
```

**Python:**
```bash
python bot.py --scheduled --image
```

Press Ctrl+C to stop.

## Easy Launch Scripts 🎯

### Linux/Mac:
```bash
./run-bot.sh
```

### Windows:
```
run-bot.bat
```

These scripts give you an interactive menu!

## Cost Breakdown 💰

### Per Tweet:
- Text only: ~$0.0001 (GPT-4 Mini)
- With image: ~$0.04 (DALL-E 3)

### Monthly (hourly posts):
- Text only: ~$7.20/month (720 tweets)
- With images: ~$28.80/month (720 tweets)

### Save Money:
- Post every 2-4 hours instead
- Use text-only mode
- Post only during active hours

## Customization Ideas 💡

### Change Tweet Format

Edit `bot.ts` or `bot.py`:

```typescript
// Change hashtags
const tweetText = `${summary}\n\n#YourHashtags #Custom\n\nSource: ${topSource}`;
```

### Change Posting Schedule

Edit `.env`:
```env
POST_INTERVAL=120  # Post every 2 hours
```

### Disable News Types

Edit `.env`:
```env
CRYPTO_NEWS_ENABLED=true
WORLD_NEWS_ENABLED=false  # Only crypto news
```

## Running 24/7 (Production) 🌐

### Using PM2 (Easiest):
```bash
npm install -g pm2
pm2 start npm --name "twitter-bot" -- run scheduled:image
pm2 save
pm2 startup  # Auto-start on reboot
```

Monitor:
```bash
pm2 logs twitter-bot
pm2 status
```

### Using Docker:
```bash
cd twitter-bot
docker build -t twitter-bot .
docker run -d --env-file .env --name twitter-bot twitter-bot
```

## Project Structure 📁

```
twitter-bot/
├── bot.ts                 # TypeScript bot (recommended)
├── bot.py                 # Python bot (alternative)
├── package.json           # Node.js config & scripts
├── requirements.txt       # Python dependencies
├── .env                   # Your credentials
├── setup-credentials.js   # Auto-setup script
├── run-bot.sh            # Linux/Mac launcher
├── run-bot.bat           # Windows launcher
├── README.md             # Full documentation
├── QUICK_START.md        # Quick guide
└── temp/                 # Generated images (auto-created)
```

## Useful Commands 📝

### TypeScript:
```bash
npm run once           # Post once (text)
npm run once:image     # Post once (with image)
npm run scheduled      # Auto-post (text)
npm run scheduled:image # Auto-post (with images)
```

### Python:
```bash
python bot.py --once              # Post once
python bot.py --once --image      # Post once with image
python bot.py --scheduled         # Auto-post
python bot.py --scheduled --image # Auto-post with images
```

## Troubleshooting 🔧

### "Error: Unauthorized"
Check Twitter credentials in `.env`. Make sure your app has "Read and Write" permissions.

### "OpenAI API Error"
Verify you have credits: https://platform.openai.com/account/billing

### "No news found"
Normal occasionally. The bot uses fallback sources automatically. Try again in a few minutes.

### Bot not posting images
Check OpenAI credits. Bot will post text-only if image generation fails.

## Next Steps 🎯

1. ✅ Run your first test tweet: `npm run once`
2. ✅ Try with an image: `npm run once:image`
3. ✅ Customize tweet format and hashtags
4. ✅ Set your posting schedule
5. ✅ Deploy to production (PM2 or Docker)
6. ✅ Monitor your Twitter engagement

## Support & Documentation 📚

- **Full README**: See `README.md` for comprehensive docs
- **Quick Start**: See `QUICK_START.md` for detailed setup
- **Twitter API Docs**: https://developer.twitter.com/docs
- **OpenAI Docs**: https://platform.openai.com/docs

## Important Notes ⚠️

1. **API Rate Limits**: Be respectful of API limits
2. **Twitter Rules**: Follow Twitter's automation rules
3. **Costs**: Monitor your OpenAI usage
4. **Testing**: Start with `--once` flag to test
5. **Backups**: Keep your `.env` file secure

## Example Tweet Output 📱

```
Bitcoin hits new ATH as institutional investors pile in. 
Ethereum follows with major upgrade announcement. 
Markets show strong bullish signals.

#Crypto #AI #News

Source: CryptoPanic
```

With an AI-generated image showing crypto charts and trends! 🎨

## Why Two Versions? 🤔

**TypeScript (Recommended if):**
- ✅ You're already using Node.js
- ✅ Better integration with your Next.js app
- ✅ Same ecosystem as your project

**Python (Choose if):**
- ✅ You prefer Python
- ✅ Easier for some to understand
- ✅ More data science libraries available

Both versions have identical features!

## Success Tips 🌟

1. **Start Small**: Test with `--once` first
2. **Monitor Costs**: Check OpenAI dashboard daily
3. **Engagement**: Post every 2-4 hours for best results
4. **Content**: Customize hashtags for your audience
5. **Quality**: Use images for 2-3x more engagement

## Ready to Go! 🎉

Your bot is ready to start posting! 

**Quick Start:**
```bash
cd twitter-bot
node setup-credentials.js
npm install
npm run once
```

That's it! Your first AI-powered tweet is about to go live! 🚀

---

**Questions?** Check README.md or QUICK_START.md for more details!

**Happy Tweeting!** 🐦✨

