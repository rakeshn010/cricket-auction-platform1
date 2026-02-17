# Cloudinary Setup Guide

## What is Cloudinary?

Cloudinary is a cloud-based image and video management service. It provides:
- **Permanent storage** for uploaded images
- **Fast CDN delivery** worldwide
- **Automatic optimization** and resizing
- **Free tier**: 25GB storage, 25GB bandwidth/month

## Why We Need It

Railway's filesystem is **ephemeral** - files uploaded during runtime are lost when the app redeploys. Cloudinary solves this by storing images in the cloud permanently.

## Setup Steps (5 minutes)

### Step 1: Create Free Account

1. Go to: https://cloudinary.com/users/register/free
2. Sign up with your email
3. Verify your email
4. Login to dashboard

### Step 2: Get Your Credentials

1. In Cloudinary dashboard, go to **Dashboard** (home page)
2. You'll see your credentials:
   - **Cloud Name**: (e.g., `dxyz123abc`)
   - **API Key**: (e.g., `123456789012345`)
   - **API Secret**: (e.g., `abcdefghijklmnopqrstuvwxyz`)

### Step 3: Add to Railway Environment Variables

1. Go to Railway dashboard: https://railway.app
2. Select your project: **intelligent-imagination**
3. Select service: **cricket-auction-platform1**
4. Go to **Variables** tab
5. Add these 3 variables:

```
CLOUDINARY_CLOUD_NAME=your_cloud_name_here
CLOUDINARY_API_KEY=your_api_key_here
CLOUDINARY_API_SECRET=your_api_secret_here
```

**IMPORTANT**: Replace the values with your actual Cloudinary credentials!

### Step 4: Redeploy

Railway will automatically redeploy when you save the environment variables.

## How It Works

### Before (Local Storage):
```
Player uploads image → Saved to /static/uploads/players/ → Lost on redeploy ❌
```

### After (Cloudinary):
```
Player uploads image → Uploaded to Cloudinary → Permanent URL → Saved in database ✅
```

## Testing

### Test Player Registration:

1. Go to: https://cricket-auction-platform1-production.up.railway.app/
2. Click "Player Registration"
3. Fill form and upload image
4. Submit
5. Image will be uploaded to Cloudinary automatically!

### Check Cloudinary Dashboard:

1. Login to Cloudinary
2. Go to **Media Library**
3. You'll see uploaded images in `cricket_auction/players/` folder

## Features

### Automatic Image Optimization:
- Images are automatically resized to 500x500px max
- Quality is optimized for web
- Format is converted if needed

### CDN Delivery:
- Images load fast from nearest server
- No load on your Railway server

### Permanent Storage:
- Images never get deleted on redeploy
- Survives Railway restarts

## Fallback Behavior

If Cloudinary is not configured:
- System falls back to local storage
- Works for development/testing
- Images will be lost on Railway redeploy

## Free Tier Limits

- **Storage**: 25 GB
- **Bandwidth**: 25 GB/month
- **Transformations**: 25,000/month
- **Images**: Unlimited

This is more than enough for your cricket auction platform!

## Troubleshooting

### Images not uploading?

1. Check Railway environment variables are set correctly
2. Check Cloudinary credentials are correct
3. Check Railway logs for errors: `railway logs`

### Still using local storage?

1. Verify environment variables in Railway
2. Redeploy the app
3. Check logs for "Cloudinary configured" message

## Cost

**Free forever** for your use case! The free tier is very generous.

If you ever exceed limits (unlikely):
- **Plus Plan**: $89/month (100GB storage, 100GB bandwidth)

## Summary

✅ **5-minute setup**  
✅ **Free forever** (for your needs)  
✅ **Images persist permanently**  
✅ **Fast CDN delivery**  
✅ **Automatic optimization**  

Just add the 3 environment variables to Railway and you're done!
