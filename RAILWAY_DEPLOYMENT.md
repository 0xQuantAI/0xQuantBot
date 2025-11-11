# Railway Deployment Guide for Twitter Bot

This guide will help you deploy the Twitter News Bot to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Account**: Your code should be in a GitHub repository
3. **API Keys**: Have your API keys ready:
   - Twitter API credentials (from [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard))
   - OpenAI API key (from [OpenAI Platform](https://platform.openai.com/api-keys))
   - NewsAPI key (optional, from [NewsAPI.org](https://newsapi.org/register))

## Deployment Steps

### Step 1: Prepare Your Repository

Ensure your `twitter-bot` directory contains:
- ✅ `bot.py` (main application)
- ✅ `requirements.txt` (Python dependencies)
- ✅ `Procfile` (start command)
- ✅ `template.png` (placeholder image)
- ✅ `.env.example` (environment variables template)

### Step 2: Create a Railway Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Select the `twitter-bot` directory as the root directory (or configure it in Railway settings)

### Step 3: Configure Environment Variables

In Railway dashboard, go to your service → **Variables** tab and add:

#### Required Variables:
```
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_token_secret
OPENAI_API_KEY=your_openai_api_key
```

#### Optional Variables:
```
NEWS_API_KEY=your_news_api_key
UPLOADME_API_KEY=your_uploadme_api_key
PLACEHOLDER_IMAGE_PATH=/app/template.png
PORT=8000
```

**Note**: Railway automatically sets `PORT` - you don't need to set it manually unless you want a specific port.

### Step 4: Configure Build Settings

Railway will auto-detect Python, but you can verify:

1. Go to **Settings** → **Build**
2. **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
3. **Start Command**: `python bot.py`

Or Railway will use the `Procfile` automatically.

### Step 5: Deploy

1. Railway will automatically start building and deploying
2. Watch the build logs for any errors
3. Once deployed, Railway will provide a public URL (e.g., `https://your-app.railway.app`)

### Step 6: Test the Deployment

1. **Health Check**: Visit `https://your-app.railway.app/health`
   - Should return: `{"status": "ok"}`

2. **Test Run Endpoint**: Use curl or Postman to test:
   ```bash
   curl -X POST https://your-app.railway.app/run \
     -H "Content-Type: application/json" \
     -d '{
       "useImage": true,
       "dryRun": true,
       "useOpenAIImageOnly": false
     }'
   ```

## Configuration Files Explained

### `Procfile`
```
web: python bot.py
```
Tells Railway how to start your application.

### `requirements.txt`
Lists all Python dependencies. Railway will install these automatically.

### `nixpacks.toml`
Custom build configuration for Railway's Nixpacks builder. Ensures Chromium is available for screenshots.

### `railway.json`
Railway-specific configuration (optional, Railway will auto-detect most settings).

## Troubleshooting

### Build Fails

1. **Check Python version**: Ensure `runtime.txt` specifies Python 3.11+
2. **Check dependencies**: Verify all packages in `requirements.txt` are valid
3. **Check logs**: Railway provides detailed build logs

### Application Crashes

1. **Check environment variables**: Ensure all required variables are set
2. **Check logs**: Railway provides runtime logs - look for error messages
3. **Test locally first**: Run `python bot.py` locally to catch issues

### Screenshot Generation Fails

1. **Chromium dependencies**: The `nixpacks.toml` ensures Chromium is installed
2. **Memory limits**: Railway free tier has memory limits - screenshots may need more memory
3. **Consider using OpenAI images only**: Set `useOpenAIImageOnly: true` to skip screenshots

### Port Issues

- Railway automatically sets `PORT` environment variable
- Your code reads `PORT` from environment (already configured in `bot.py`)
- Don't hardcode port numbers

## Monitoring

1. **Logs**: View real-time logs in Railway dashboard
2. **Metrics**: Check CPU/Memory usage in Railway dashboard
3. **Health Checks**: Set up monitoring for `/health` endpoint

## Scheduling Posts

To schedule posts, you can:

1. **External Cron Service**: Use services like:
   - [cron-job.org](https://cron-job.org)
   - [EasyCron](https://www.easycron.com)
   - [GitHub Actions](https://github.com/features/actions)

2. **Example Cron Job**:
   ```bash
   # Post every hour
   0 * * * * curl -X POST https://your-app.railway.app/run -H "Content-Type: application/json" -d '{"useImage": true, "dryRun": false}'
   ```

3. **GitHub Actions Example**:
   Create `.github/workflows/twitter-bot.yml`:
   ```yaml
   name: Twitter Bot Post
   on:
     schedule:
       - cron: '0 * * * *'  # Every hour
   jobs:
     post:
       runs-on: ubuntu-latest
       steps:
         - name: Trigger Bot
           run: |
             curl -X POST ${{ secrets.RAILWAY_URL }}/run \
               -H "Content-Type: application/json" \
               -d '{"useImage": true, "dryRun": false}'
   ```

## Updating the Deployment

1. **Push to GitHub**: Railway auto-deploys on push to main branch
2. **Manual Deploy**: Use Railway dashboard to trigger redeploy
3. **Rollback**: Use Railway dashboard to rollback to previous deployment

## Cost Considerations

- **Railway Free Tier**: $5 credit/month
- **Usage**: Monitor your usage in Railway dashboard
- **Optimization**: Consider using `useOpenAIImageOnly: true` to reduce memory usage

## Security Best Practices

1. **Never commit `.env`**: Already in `.gitignore`
2. **Use Railway Secrets**: Store sensitive keys in Railway Variables (encrypted)
3. **Rotate Keys**: Regularly rotate API keys
4. **Monitor Logs**: Check logs for any exposed credentials

## Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **Check Logs**: Always check Railway logs first for errors

## Quick Reference

### Endpoints

- `GET /health` - Health check
- `POST /run` - Trigger bot run

### Request Body for `/run`:
```json
{
  "useImage": true,
  "dryRun": false,
  "useOpenAIImageOnly": false,
  "cryptoNewsEnabled": true,
  "worldNewsEnabled": true,
  "credentials": {
    "twitterApiKey": "...",
    "twitterApiSecret": "...",
    "twitterAccessToken": "...",
    "twitterAccessSecret": "...",
    "openaiApiKey": "..."
  }
}
```

### Response:
```json
{
  "success": true,
  "tweetId": "1234567890",
  "tweetText": "...",
  "imageUrl": "..."
}
```

---

**Ready to deploy?** Follow the steps above and your bot will be live on Railway! 🚀

