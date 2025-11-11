# Railway Deployment Checklist

## ✅ Files Created/Updated

### Deployment Configuration Files:
- ✅ `Procfile` - Tells Railway how to start the app
- ✅ `runtime.txt` - Specifies Python 3.11.9
- ✅ `nixpacks.toml` - Build config with Chromium for screenshots
- ✅ `railway.json` - Railway-specific configuration
- ✅ `.dockerignore` - Optimizes build by excluding unnecessary files

### Documentation:
- ✅ `RAILWAY_DEPLOYMENT.md` - Complete deployment guide
- ✅ `QUICK_DEPLOY.md` - Quick start guide

### Updated Files:
- ✅ `requirements.txt` - Added `httpx>=0.24.0` (required for OpenAI)
- ✅ `.gitignore` - Updated to allow `template.png` in git

### Required Files (Already Present):
- ✅ `bot.py` - Main application
- ✅ `template.png` - Background image
- ✅ `.env.example` - Environment variables template

## 📋 Pre-Deployment Checklist

### 1. Verify Files Are Committed
```bash
cd twitter-bot
git status
# Ensure template.png is tracked (not ignored)
git add template.png
git add Procfile runtime.txt nixpacks.toml railway.json
git add requirements.txt .gitignore
git commit -m "Add Railway deployment configuration"
```

### 2. Push to GitHub
```bash
git push origin main
```

### 3. Prepare Environment Variables
Have these ready:
- [ ] `TWITTER_API_KEY`
- [ ] `TWITTER_API_SECRET`
- [ ] `TWITTER_ACCESS_TOKEN`
- [ ] `TWITTER_ACCESS_SECRET`
- [ ] `OPENAI_API_KEY`
- [ ] `NEWS_API_KEY` (optional)
- [ ] `UPLOADME_API_KEY` (optional)

## 🚀 Deployment Steps

1. **Create Railway Project**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

2. **Configure Root Directory** (if needed)
   - If your repo root is not `twitter-bot`, set root directory in Railway settings
   - Go to Settings → Root Directory → Set to `twitter-bot`

3. **Set Environment Variables**
   - Go to Variables tab
   - Add all required variables from checklist above

4. **Deploy**
   - Railway will auto-detect and start building
   - Watch build logs for any errors
   - Wait for deployment to complete

5. **Test**
   - Visit `https://your-app.railway.app/health`
   - Should return `{"status": "ok"}`

## 🔍 Verification

After deployment, test with:

```bash
# Health check
curl https://your-app.railway.app/health

# Test bot (dry run)
curl -X POST https://your-app.railway.app/run \
  -H "Content-Type: application/json" \
  -d '{
    "useImage": true,
    "dryRun": true,
    "useOpenAIImageOnly": false
  }'
```

## 📝 Post-Deployment

1. **Set Up Scheduling** (optional)
   - Use external cron service
   - Or GitHub Actions
   - See `RAILWAY_DEPLOYMENT.md` for examples

2. **Monitor**
   - Check Railway logs regularly
   - Monitor resource usage
   - Set up alerts if needed

## 🆘 Troubleshooting

If deployment fails:

1. **Check Build Logs**
   - Look for Python version issues
   - Check dependency installation errors

2. **Check Runtime Logs**
   - Look for missing environment variables
   - Check for import errors

3. **Verify Files**
   - Ensure `template.png` is in repository
   - Verify `requirements.txt` is correct
   - Check `Procfile` syntax

4. **Common Issues**
   - **Port errors**: Railway sets PORT automatically, don't override
   - **Memory issues**: Consider upgrading Railway plan
   - **Screenshot failures**: Ensure Chromium is installed (handled by nixpacks.toml)

## 📚 Documentation

- Full guide: `RAILWAY_DEPLOYMENT.md`
- Quick start: `QUICK_DEPLOY.md`
- Railway docs: [docs.railway.app](https://docs.railway.app)

---

**Ready to deploy?** Follow the steps above! 🚀

