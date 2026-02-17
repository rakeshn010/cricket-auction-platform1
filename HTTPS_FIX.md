# HTTPS/CSP Mixed Content Fix

## Problem
Players were not displaying in the admin panel due to Content Security Policy (CSP) violations. The browser was blocking HTTP requests made from an HTTPS page.

### Error Messages
```
Connecting to 'http://cricket-auction-platform1-production.up.railway.app/players/?include_unapproved=true' 
violates the following Content Security Policy directive: "connect-src 'self' ws: wss: ..."
```

```
Mixed Content: The page at 'https://...' was loaded over HTTPS, but attempted to connect to 
the insecure WebSocket endpoint 'ws://...'
```

## Root Cause
The JavaScript `api()` functions in `admin.js` and `team_dashboard_new.js` were not properly forcing HTTPS for relative URLs. The condition `url.startsWith('/') && window.location.protocol === 'https:'` was not catching all cases.

## Solution

### 1. Fixed `api()` Function Logic
Changed from checking if URL starts with `/` to checking if it doesn't start with `http://` or `https://`:

**Before:**
```javascript
if (url.startsWith('http://')) {
    url = url.replace('http://', 'https://');
} else if (url.startsWith('/') && window.location.protocol === 'https:') {
    url = `https://${window.location.host}${url}`;
}
```

**After:**
```javascript
if (!url.startsWith('http://') && !url.startsWith('https://')) {
    // Relative URL - construct absolute HTTPS URL
    url = `https://${window.location.host}${url}`;
} else if (url.startsWith('http://')) {
    // Force HTTPS
    url = url.replace('http://', 'https://');
}
```

### 2. Fixed WebSocket Connection in team_dashboard_new.js
Changed from hardcoded `ws://` to protocol-aware `wss://`:

**Before:**
```javascript
const wsUrl = `ws://${window.location.host}/auction/ws`;
```

**After:**
```javascript
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${protocol}//${window.location.host}/auction/ws`;
```

## Files Modified
- `static/admin.js` - Fixed `api()` function
- `static/team_dashboard_new.js` - Fixed `api()` function and WebSocket connection

## Files Already Correct
- `static/live_studio.js` - Already using protocol-aware WebSocket connection

## Testing
After deployment:
1. Open admin panel at `https://cricket-auction-platform1-production.up.railway.app/admin`
2. Check browser console - should see "Constructed HTTPS URL: https://..." messages
3. No CSP violation errors should appear
4. Players should load and display correctly
5. WebSocket should connect using `wss://`

## Status
✅ Changes committed and pushed to GitHub
✅ Railway will auto-deploy
⏳ Wait 2-3 minutes for deployment
🔄 Hard refresh browser (Ctrl+Shift+R) to clear cached JavaScript files
