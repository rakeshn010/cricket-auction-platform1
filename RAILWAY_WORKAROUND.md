# Railway Deployment Workaround

## Issue: Can't Add Environment Variables in Railway UI

If you're getting "Failed to fetch" error when adding variables, here's the workaround:

## Solution: Deploy First, Add Variables Later via CLI

### Step 1: Push Code Changes
```bash
git add .
git commit -m "Make MongoDB connection optional for Railway"
git push
```

This will trigger Railway to deploy. The app will start even without MongoDB (it will just log a warning).

### Step 2: Install Railway CLI
```bash
npm install -g @railway/cli
```

If you don't have npm, download from: https://nodejs.org/

### Step 3: Login and Link Project
```bash
# Login to Railway
railway login

# Link to your project (select from list)
railway link
```

### Step 4: Add Environment Variables via CLI
```bash
# Generate JWT secret
railway variables set JWT_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"

# Add MongoDB URL (get from MongoDB Atlas)
railway variables set MONGODB_URL="mongodb+srv://username:password@cluster.mongodb.net/cricket_auction"

# Set environment
railway variables set ENVIRONMENT="production"
railway variables set DEBUG="false"

# Optional: Set CORS for your Railway domain
railway variables set CORS_ORIGINS="https://your-app.railway.app"
```

### Step 5: Verify Variables
```bash
railway variables
```

### Step 6: Check Logs
```bash
railway logs
```

## Alternative: Use Railway's Raw Editor

If CLI doesn't work, try the Raw Editor in Railway dashboard:

1. Go to your service → Variables tab
2. Click "RAW Editor" (top right corner)
3. Paste this (replace with your values):
```
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/cricket_auction
JWT_SECRET=your-generated-secret-here
ENVIRONMENT=production
DEBUG=false
```
4. Click outside the editor to save

## MongoDB Atlas Setup (Required)

1. Go to https://cloud.mongodb.com/
2. Create free account
3. Create M0 FREE cluster (512MB)
4. Database Access → Add User (username/password)
5. Network Access → Add IP: `0.0.0.0/0` (allow all - required for Railway)
6. Get connection string:
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your actual password
   - Replace `<dbname>` with `cricket_auction`

Example: `mongodb+srv://myuser:mypass123@cluster0.xxxxx.mongodb.net/cricket_auction?retryWrites=true&w=majority`

## Test Deployment

Once variables are set, Railway will auto-redeploy. Check logs:
```bash
railway logs
```

Look for:
- ✅ "Connected to MongoDB: cricket_auction"
- ✅ "Application startup complete"
- ✅ "Uvicorn running on http://0.0.0.0:XXXX"

## Access Your App

Your app URL: `https://your-project-name.railway.app`

Login: `admin@cricket.com` / `admin123`

## If Still Having Issues

1. Check Railway status: https://status.railway.app/
2. Try different browser or incognito mode
3. Clear browser cache
4. Wait 5-10 minutes (Railway sometimes has temporary issues)
5. Contact Railway support: https://railway.app/help

---

**Current Status**: App will deploy and start without MongoDB, but you need to add MONGODB_URL for it to work properly.
