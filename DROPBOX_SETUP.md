# Dropbox Setup Guide - Image Hosting for X API Free Tier 📦

## Why Dropbox? 🤔

You're on X API **Free tier** which blocks direct media uploads. The solution:
1. Upload images to Dropbox (free, 2GB storage)
2. Get public share link
3. Include link in tweet
4. X automatically shows preview

**Result**: Your tweets show images even on Free tier! ✅

## Quick Setup (3 minutes) ⚡

### Step 1: Create Dropbox Account (if needed)
Go to: https://www.dropbox.com/register
- Sign up with email or Google
- Free account gives 2GB storage
- More than enough for thousands of images

### Step 2: Create Dropbox App

1. Go to: **https://www.dropbox.com/developers/apps**
2. Click **"Create app"**
3. Configure:
   - **Choose an API**: Select **"Scoped access"**
   - **Choose the type of access**: Select **"Full Dropbox"**
   - **Name your app**: `0xQuant Twitter Bot` (or any name)
4. Click **"Create app"**

### Step 3: Configure Permissions

On your app's page:

1. Go to **"Permissions"** tab
2. Enable these permissions:
   - ✅ `files.content.write` - Upload files
   - ✅ `files.content.read` - Access files
   - ✅ `sharing.write` - Create shared links
3. Click **"Submit"** at the bottom

### Step 4: Generate Access Token

1. Go to **"Settings"** tab
2. Scroll to **"OAuth 2"** section
3. Under **"Generated access token"**:
   - Click **"Generate"** button
   - Copy the token (long string starting with `sl.`)
   - ⚠️ **Save it immediately** - you won't see it again!

Example token:
```
sl.B1234567890abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrs
```

### Step 5: Add to Bot Configuration

Edit `twitter-bot/.env`:

```env
# Dropbox Access Token (for image hosting)
DROPBOX_ACCESS_TOKEN=sl.B1234567890abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrs
```

Replace with your actual token from Step 4.

### Step 6: Test!

```bash
cd twitter-bot
npm run once:image
```

You should see:
```
🎨 Generating image with DALL-E...
   ✓ Image generated: temp/news_1234567890.png
   ⚠ Direct media upload failed (Free tier limitation)
   → Using Dropbox fallback...
   ✓ Uploaded to Dropbox: /twitter-bot/news_1234567890.png
   ✓ Public URL: https://dl.dropboxusercontent.com/...
🐦 Posting to Twitter...
   ✓ Tweet posted successfully!
```

## How It Works 🔧

```
1. Bot generates image with DALL-E ✅
2. Try direct upload to X → 403 Forbidden ❌
3. Upload to Dropbox instead → Success ✅
4. Create public shared link ✅
5. Include Dropbox URL in tweet text ✅
6. X shows automatic preview 🖼️
```

**User Experience**: Same as direct upload! X previews look identical.

## Example Tweet Output 📱

**What gets posted:**
```
Bitcoin reaches new ATH as institutional investors pile in. 
Ethereum follows with major upgrades. Markets bullish!

#Crypto #AI #News

Source: CryptoPanic
https://dl.dropboxusercontent.com/s/abc123/news_1234567890.png?raw=1
```

**What users see**: Tweet with embedded image preview (looks native!)

## Dropbox Free Tier Limits ✨

| Feature | Free Tier |
|---------|-----------|
| **Storage** | 2 GB |
| **File Size** | No limit (within storage) |
| **API Calls** | Reasonable use |
| **Bandwidth** | Fair use policy |
| **Cost** | $0 |

**Your usage**: 
- ~1 MB per image × 10 images/day = 10 MB/day
- 2 GB = 2,000 MB → **200 days** of storage!
- Or upgrade to Plus (2 TB) for $9.99/month

## Dropbox vs Other Services

| Service | Free Storage | API Limits | Setup Time | Cost |
|---------|--------------|------------|------------|------|
| **Dropbox** | 2 GB | Fair use | 3 min | $0 |
| **Imgur** | Unlimited | 12,500/day | 2 min | $0 |
| **X Elevated** | N/A | Direct upload | 1-3 days | $0 |

**Why Dropbox?**
- ✅ More professional (your own storage)
- ✅ Better privacy control
- ✅ Easy file management
- ✅ Organized in folders
- ✅ Can access/delete files anytime

## Commands 🎯

```bash
# Test with Dropbox fallback
npm run once:image

# Schedule posts with images
npm run scheduled:image

# Check if Dropbox is configured
node -e "require('dotenv').config(); console.log('Dropbox:', process.env.DROPBOX_ACCESS_TOKEN ? '✓ Configured' : '✗ Not set')"
```

## Troubleshooting 🔧

### "Dropbox authentication failed: Invalid access token"

**Problem**: Wrong token or expired
**Solution**: 
1. Go back to https://www.dropbox.com/developers/apps
2. Click your app
3. Settings tab → Generate new access token
4. Update `.env` file

### "Permission denied"

**Problem**: Missing permissions on app
**Solution**:
1. Go to your app's Permissions tab
2. Enable: `files.content.write`, `files.content.read`, `sharing.write`
3. Click Submit
4. Regenerate access token (permissions apply to new tokens only)

### "Storage full"

**Problem**: Exceeded 2 GB free storage
**Solution**:
1. Go to https://www.dropbox.com/home/twitter-bot
2. Delete old images you don't need
3. Or upgrade to Dropbox Plus (2 TB for $9.99/month)

### Still posting text-only

**Problem**: DROPBOX_ACCESS_TOKEN not set correctly
**Solution**: Check `.env` file has actual token:
```env
# Wrong:
DROPBOX_ACCESS_TOKEN=your_dropbox_access_token_here

# Correct (starts with sl.):
DROPBOX_ACCESS_TOKEN=sl.B1234567890abcdef...
```

## Verify Setup ✅

Run this to check configuration:

```bash
cd twitter-bot
node -e "
require('dotenv').config();
const token = process.env.DROPBOX_ACCESS_TOKEN;
console.log('Dropbox Token:', token ? '✓ Set (' + token.substring(0, 8) + '...)' : '✗ Not configured');
console.log('Status:', token && token !== 'your_dropbox_access_token_here' ? '✅ Ready for image posts!' : '⚠️ Configure DROPBOX_ACCESS_TOKEN in .env');
"
```

## File Organization 📁

Your images are stored in Dropbox at:
```
/twitter-bot/
  ├── news_1234567890.png
  ├── news_1234567891.png
  └── news_1234567892.png
```

You can:
- View all images in Dropbox web/app
- Download them anytime
- Delete old ones to free space
- Organize into subfolders

## Security & Privacy 🔒

**Access Token Security**:
- ✅ Keep in `.env` file (in `.gitignore`)
- ✅ Never commit to public repos
- ✅ Regenerate if compromised
- ⚠️ Gives full Dropbox access - keep secure!

**Image Privacy**:
- 🔓 Shared links are public (anyone with link can view)
- ✅ Not listed publicly (need exact URL)
- ✅ Can revoke shared links anytime
- ✅ Can delete images from Dropbox

## When to Use vs X Elevated Access

| Scenario | Use Dropbox | Apply for Elevated |
|----------|-------------|-------------------|
| Need images NOW | ✅ | ⏳ Wait 1-3 days |
| Want file control | ✅ | ❌ |
| Privacy conscious | ✅ | ⚠️ On X servers |
| Long-term solution | ✅ | ✅ Recommended |
| Zero cost | ✅ | ✅ |

**Best approach**: Use Dropbox now, apply for Elevated too!

## Storage Management Tips 💡

**Keep storage under 2 GB**:

1. **Auto-delete old images** (optional script):
```bash
# Delete images older than 30 days
find temp/ -name "news_*.png" -mtime +30 -delete
```

2. **Monitor storage**:
   - Check: https://www.dropbox.com/account
   - Used: ~1 MB per image
   - 2 GB = ~2,000 images

3. **Clean Dropbox folder**:
   - Keep last 90 days (free)
   - Or upgrade to Plus ($9.99/mo for 2 TB)

## Automatic Failover 🔄

Your bot now has smart failover:

```
Try Method 1: Direct upload to X
  ↓ If fails (403 Forbidden)
Try Method 2: Upload to Dropbox, include URL
  ↓ If fails
Fallback: Text-only post
```

**Always posts something!** 💪

## After Getting X Elevated Access ⚡

Once X approves your Elevated access:

1. **No code changes needed**
2. Bot automatically uses direct upload
3. Dropbox as backup if direct fails
4. Images stored on X (better) + Dropbox backup (optional)

## Advanced: Custom Folder Structure

Want to organize by date? Modify `dropbox-helper.ts`:

```typescript
// Current:
const dropboxPath = `/twitter-bot/${fileName}`;

// By date:
const date = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
const dropboxPath = `/twitter-bot/${date}/${fileName}`;
```

## Cost Comparison 💰

| Solution | Setup Time | Monthly Cost | Storage | Works Now |
|----------|------------|--------------|---------|-----------|
| **Dropbox** | 3 minutes | $0 | 2 GB | ✅ Yes |
| **Dropbox Plus** | 3 minutes | $9.99 | 2 TB | ✅ Yes |
| **X Elevated** | 5 min + wait | $0 | N/A | ⏳ 1-3 days |
| **X Basic** | 2 minutes | $100 | N/A | ✅ Yes |

## Next Steps 🎯

**Right now** (3 minutes):
1. ✅ Create Dropbox app: https://www.dropbox.com/developers/apps
2. ✅ Enable permissions
3. ✅ Generate access token
4. ✅ Add to `.env`
5. ✅ Test: `npm run once:image`

**For future**:
1. ⏳ Apply for X Elevated access (also free, no rush)
2. ⏳ Wait for approval (1-3 days)
3. ✅ Bot automatically upgrades to direct upload

## Summary 📋

✅ **Works with X API Free tier**
✅ **2 GB free storage (2,000+ images)**
✅ **3-minute setup**
✅ **Images look native on X**
✅ **Full control over your files**
✅ **Automatic failover**
✅ **Professional file management**

---

**Quick Start**:
```bash
# 1. Create app: https://www.dropbox.com/developers/apps
# 2. Enable permissions: files.content.write, sharing.write
# 3. Generate token in Settings tab
# 4. Add to twitter-bot/.env:
DROPBOX_ACCESS_TOKEN=sl.your_token_here

# 5. Test
npm run once:image
```

Your images will now work on X API Free tier with professional Dropbox storage! 🎉

---

## Bonus: Test Connection

Before your first post, test the connection:

```bash
cd twitter-bot
node -e "
const { testDropboxConnection } = require('./dropbox-helper');
require('dotenv').config();

testDropboxConnection(process.env.DROPBOX_ACCESS_TOKEN).then(result => {
  console.log(result ? '✅ Dropbox ready!' : '❌ Connection failed');
});
"
```

Happy tweeting with Dropbox! 📦✨

