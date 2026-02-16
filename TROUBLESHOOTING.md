# Cricket Auction Platform - Troubleshooting Guide

## Common Issues & Solutions

---

## 🔒 Content Security Policy (CSP) Errors

### Issue: CDN Resources Blocked

**Error Messages**:
```
Loading the stylesheet 'https://cdnjs.cloudflare.com/...' violates the following 
Content Security Policy directive: "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net"
```

**Cause**: CSP is blocking external CDN resources for security.

**Solution**: ✅ FIXED - Updated CSP to allow common CDNs:
- `https://cdn.jsdelivr.net`
- `https://cdnjs.cloudflare.com`

**Current CSP Policy**:
```
script-src: 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net cdnjs.cloudflare.com
style-src: 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com
font-src: 'self' data: cdn.jsdelivr.net cdnjs.cloudflare.com
connect-src: 'self' ws: wss: cdn.jsdelivr.net cdnjs.cloudflare.com
```

**If You Need to Add More CDNs**:
Edit `core/security_middleware.py`, line ~30:
```python
response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://YOUR_CDN_HERE; "
    # ... add your CDN to each directive as needed
)
```

---

## 🔐 Authentication Errors

### Issue: 401 Unauthorized on Login

**Error**: `Failed to load resource: the server responded with a status of 401 (Unauthorized)`

**Common Causes**:

#### 1. Wrong Credentials
**Solution**: Verify you're using correct credentials:
- Email: `admin@cricket.com`
- Password: `admin123`

#### 2. Email Case Sensitivity
**Solution**: Email is automatically converted to lowercase. Use lowercase email.

#### 3. User Doesn't Exist
**Solution**: Create admin user:
```bash
venv\Scripts\python create_admin.py
```

#### 4. Account Disabled
**Check**: User's `is_active` field in database
**Solution**: Update in MongoDB:
```javascript
db.users.updateOne(
    {email: "admin@cricket.com"},
    {$set: {is_active: true}}
)
```

#### 5. Password Hash Mismatch
**Solution**: Reset admin account using the utility script:
```bash
venv\Scripts\python reset_admin.py
```

This will:
- Delete existing admin user
- Create new admin with correct password hash
- Verify password works

**Alternative**: Manually reset in MongoDB:
```bash
# Delete existing user
mongosh
use cricket_auction
db.users.deleteOne({email: "admin@cricket.com"})

# Recreate
venv\Scripts\python create_admin.py
```

#### 6. Test Login Credentials
**Verify credentials work**:
```bash
venv\Scripts\python test_login.py
```

This will show:
- If admin user exists
- If password hash is correct
- Account status

### Issue: Multiple 401 Errors in Console

**Cause**: This is NORMAL if:
- User entered wrong password
- Testing authentication
- Rate limiting kicked in

**When to Worry**: Only if you can't login with correct credentials.

**Debug Steps**:
1. Check server logs: `type logs\app.log`
2. Verify MongoDB is running
3. Check user exists in database
4. Try creating a new user

---

## 🌐 CORS Errors

### Issue: CORS Policy Blocking Requests

**Error**: `Access to fetch at 'http://localhost:8000/...' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solution**: Add your frontend origin to `.env`:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000
```

**For Development** (Allow All):
```env
CORS_ORIGINS=*
```

**For Production** (Specific Origins):
```env
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## ⚡ Rate Limiting Errors

### Issue: 429 Too Many Requests

**Error**: `Rate limit exceeded. Try again in X seconds.`

**Causes**:
1. **Bidding**: More than 10 bids per minute
2. **Login**: More than 5 attempts per 5 minutes
3. **API**: More than 100 requests per minute

**Solutions**:

#### Temporary (Wait):
Check the `Retry-After` header and wait.

#### Disable Rate Limiting (Development Only):
In `.env`:
```env
ENABLE_RATE_LIMITING=false
```

Restart server.

#### Adjust Limits (Production):
Edit `core/rate_limiter.py`:
```python
# For bidding
await self.check_rate_limit(
    identifier=user_id,
    limit=20,  # Increase from 10 to 20
    window_seconds=60,
    limit_type="bid"
)
```

---

## 🔌 WebSocket Errors

### Issue: WebSocket Connection Fails

**Error**: Connection closes immediately or `1008 Policy Violation`

**Causes**:

#### 1. Missing Authentication
**Solution**: Include JWT token:
```javascript
const token = localStorage.getItem('access_token');
const ws = new WebSocket(`ws://localhost:8000/auction/ws?token=${token}`);
```

#### 2. Expired Token
**Solution**: Refresh token before connecting:
```javascript
// Refresh token first
const refreshResponse = await fetch('/auth/refresh', {
    method: 'POST',
    body: new URLSearchParams({refresh_token: refreshToken})
});
const {access_token} = await refreshResponse.json();

// Then connect
const ws = new WebSocket(`ws://localhost:8000/auction/ws?token=${access_token}`);
```

#### 3. Invalid Token Format
**Solution**: Ensure token is just the JWT string, not "Bearer <token>"

### Issue: WebSocket Disconnects Randomly

**Cause**: Heartbeat timeout or network issues

**Solution**: Implement ping-pong:
```javascript
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'ping') {
        ws.send(JSON.stringify({type: 'pong'}));
    }
};

// Reconnect on close
ws.onclose = () => {
    console.log('Disconnected, reconnecting...');
    setTimeout(connectWebSocket, 1000);
};
```

---

## 💾 Database Errors

### Issue: MongoDB Connection Failed

**Error**: `Failed to connect to MongoDB`

**Solutions**:

#### 1. MongoDB Not Running
```bash
# Check if running
mongod --version

# Start MongoDB
mongod
```

#### 2. Wrong Connection String
Check `.env`:
```env
DATABASE_URL=mongodb://localhost:27017
DB_NAME=cricket_auction
```

#### 3. MongoDB Authentication
If MongoDB has auth enabled:
```env
DATABASE_URL=mongodb://username:password@localhost:27017
```

### Issue: Duplicate Key Error

**Error**: `E11000 duplicate key error`

**Cause**: Trying to create user/team with existing email/name

**Solution**: Use unique email/name or delete existing:
```javascript
mongosh
use cricket_auction
db.users.deleteOne({email: "duplicate@email.com"})
```

---

## 📁 File Upload Errors

### Issue: File Upload Fails

**Error**: `413 Request Entity Too Large`

**Cause**: File exceeds 10MB limit

**Solution**: Increase limit in `.env`:
```env
MAX_UPLOAD_SIZE=20971520  # 20MB in bytes
```

Or in `core/security_middleware.py`:
```python
if content_length and int(content_length) > 20 * 1024 * 1024:  # 20MB
```

### Issue: Invalid File Type

**Solution**: Check allowed extensions in upload endpoint.

---

## 🎯 Bidding Errors

### Issue: Bid Rejected - "Auction is not active"

**Solution**: Start auction first:
```bash
# As admin
POST /auction/start
```

### Issue: Bid Rejected - "Insufficient budget"

**Solution**: Check team budget:
```bash
GET /teams/{team_id}
```

Increase budget if needed (admin only):
```bash
PATCH /teams/{team_id}
{
    "budget": 100000
}
```

### Issue: Bid Rejected - "Bid must be higher than current highest bid"

**Solution**: Check current bid and increase your bid amount:
```bash
GET /auction/current_player
```

---

## 🖥️ Server Errors

### Issue: Server Won't Start

**Error**: `Address already in use`

**Solution**: Kill existing process:
```bash
# Find process on port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Issue: Import Errors

**Error**: `ModuleNotFoundError: No module named 'X'`

**Solution**: Reinstall dependencies:
```bash
venv\Scripts\pip install -r requirements.txt
```

### Issue: Python Version Error

**Error**: `SyntaxError` or version-related errors

**Solution**: Ensure Python 3.11+:
```bash
python --version
```

---

## 🔍 Debugging Tips

### Enable Debug Mode

In `.env`:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

### Check Logs

```bash
# View all logs
type logs\app.log

# View last 50 lines
Get-Content logs\app.log -Tail 50

# Follow logs in real-time
Get-Content logs\app.log -Wait -Tail 50
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# API documentation
# Open in browser: http://localhost:8000/docs

# Test authentication
curl -X POST http://localhost:8000/auth/login ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "email=admin@cricket.com&password=admin123"
```

### Check Database

```bash
mongosh
use cricket_auction

# List all users
db.users.find().pretty()

# List all teams
db.teams.find().pretty()

# List all players
db.players.find().pretty()

# Check auction config
db.config.find({key: "auction"}).pretty()
```

---

## 🚨 Emergency Fixes

### Reset Everything

```bash
# Stop server
# Ctrl+C or kill process

# Drop database
mongosh
use cricket_auction
db.dropDatabase()

# Recreate admin
venv\Scripts\python create_admin.py

# Restart server
venv\Scripts\python main_new.py
```

### Disable All Security Features

In `.env` (DEVELOPMENT ONLY):
```env
ENABLE_RATE_LIMITING=false
ENABLE_CSRF_PROTECTION=false
ENABLE_IP_WHITELIST=false
CORS_ORIGINS=*
```

### Rollback Enhancements

If enhancements cause issues, you can disable them:

1. Comment out middleware in `main_new.py`:
```python
# app.add_middleware(SecurityHeadersMiddleware)
# app.add_middleware(RequestValidationMiddleware)
# app.add_middleware(AuditLogMiddleware)
```

2. Disable rate limiting in `.env`:
```env
ENABLE_RATE_LIMITING=false
```

---

## 📞 Getting Help

### Information to Provide:

1. **Error Message**: Full error from console/logs
2. **Server Logs**: Last 50 lines from `logs/app.log`
3. **Environment**: Python version, OS, MongoDB version
4. **Configuration**: Relevant `.env` settings
5. **Steps to Reproduce**: What you did before error occurred

### Useful Commands:

```bash
# System info
python --version
mongod --version

# Server status
curl http://localhost:8000/health

# Check if port is in use
netstat -ano | findstr :8000

# View recent logs
Get-Content logs\app.log -Tail 50
```

---

## ✅ Quick Fixes Checklist

When something goes wrong, try these in order:

- [ ] Check server is running: `curl http://localhost:8000/health`
- [ ] Check MongoDB is running: `mongod --version`
- [ ] Check logs: `type logs\app.log`
- [ ] Verify credentials: `admin@cricket.com` / `admin123`
- [ ] Clear browser cache and cookies
- [ ] Restart server
- [ ] Check `.env` configuration
- [ ] Verify database has data
- [ ] Test with API docs: http://localhost:8000/docs
- [ ] Check for port conflicts

---

**Last Updated**: February 16, 2026
**Version**: 1.0.0 (Enhanced)
