# Railway Quick Start Guide

## 🚀 Quick Deployment (5 minutes)

### 1. Push to GitHub
```bash
cd twitter-bot
git add .
git commit -m "Prepare for Railway deployment"
git push
```

### 2. Deploy on Railway
1. Go to [railway.app](https://railway.app)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Railway will auto-detect Python and start building

### 3. Set Environment Variables
In Railway dashboard → **Variables** tab, add:

```
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_SECRET=your_secret
OPENAI_API_KEY=your_key
```

### 4. Test
Visit: `https://your-app.railway.app/health`

Should return: `{"status": "ok"}`

### 5. Trigger Bot
```bash
curl -X POST https://your-app.railway.app/run \
  -H "Content-Type: application/json" \
  -d '{"useImage": true, "dryRun": true}'
```

## 📋 Files Included

- ✅ `bot.py` - Main application
- ✅ `requirements.txt` - Dependencies
- ✅ `Procfile` - Start command
- ✅ `template.png` - Background image
- ✅ `nixpacks.toml` - Build config (includes Chromium)
- ✅ `railway.json` - Railway config

## 🔧 Configuration

All configuration is done via environment variables. See `RAILWAY_DEPLOYMENT.md` for full details.

## 📚 Full Documentation

See `RAILWAY_DEPLOYMENT.md` for complete deployment guide.

