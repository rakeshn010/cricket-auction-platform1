# 🚦 Rate Limiting Guide

## Understanding Rate Limits

Rate limiting protects your platform from abuse by limiting how many requests a user can make in a given time period.

---

## 📊 Current Rate Limits

### Authentication (Login/Register)
- **Limit**: 10 attempts per 5 minutes per IP
- **Purpose**: Prevents brute force attacks
- **Error**: `429 Too Many Requests`
- **Message**: "Too many login attempts. Please wait X seconds."

### Bidding
- **Limit**: 10 bids per minute per user
- **Purpose**: Prevents spam bidding
- **Error**: `429 Too Many Requests`
- **Message**: "Too many bids. Please wait X seconds."

### General API
- **Limit**: 100 requests per minute per user
- **Purpose**: Prevents API abuse
- **Error**: `429 Too Many Requests`
- **Message**: "Rate limit exceeded. Please wait X seconds."

---

## 🔓 What to Do If You Get Rate Limited

### Option 1: Wait (Recommended)
```
Rate limits automatically expire:
- Authentication: 5 minutes
- Bidding: 1 minute
- General API: 1 minute

Just wait and try again!
```

### Option 2: Restart Server (Clears All Limits)
```bash
# Stop server (Ctrl+C in terminal)
# Start again
venv\Scripts\python main_new.py
```

### Option 3: Disable Rate Limiting (Development Only)
```bash
# Edit .env file
ENABLE_RATE_LIMITING=false

# Restart server
venv\Scripts\python main_new.py
```

### Option 4: Run Clear Script
```bash
venv\Scripts\python clear_rate_limits.py
```

---

## 🎯 Rate Limit Response

When you hit a rate limit, you'll receive:

```json
{
    "detail": "Too many login attempts. Please wait 245 seconds.",
    "headers": {
        "Retry-After": "245"
    }
}
```

**Status Code**: `429 Too Many Requests`

**Retry-After Header**: Tells you how many seconds to wait

---

## 💡 Best Practices

### For Users
1. ✅ Don't spam login attempts
2. ✅ Wait for error messages
3. ✅ Check credentials before retrying
4. ✅ Use "Forgot Password" if needed

### For Developers
1. ✅ Handle 429 errors gracefully
2. ✅ Show user-friendly messages
3. ✅ Implement retry logic with backoff
4. ✅ Display countdown timer

---

## 🔧 Adjusting Rate Limits

### For Development (More Lenient)

Edit `core/rate_limiter.py`:

```python
# Authentication - More attempts
async def check_auth_rate_limit(self, ip: str) -> bool:
    return await self.check_rate_limit(
        identifier=ip,
        limit=20,  # Increase from 10 to 20
        window_seconds=300,
        limit_type="ip"
    )

# Bidding - More bids
async def check_bid_rate_limit(self, user_id: str) -> bool:
    return await self.check_rate_limit(
        identifier=user_id,
        limit=20,  # Increase from 10 to 20
        window_seconds=60,
        limit_type="bid"
    )
```

### For Production (More Strict)

```python
# Authentication - Fewer attempts
async def check_auth_rate_limit(self, ip: str) -> bool:
    return await self.check_rate_limit(
        identifier=ip,
        limit=5,  # Decrease to 5
        window_seconds=300,
        limit_type="ip"
    )

# Bidding - Fewer bids
async def check_bid_rate_limit(self, user_id: str) -> bool:
    return await self.check_rate_limit(
        identifier=user_id,
        limit=5,  # Decrease to 5
        window_seconds=60,
        limit_type="bid"
    )
```

---

## 🛡️ Why Rate Limiting is Important

### Prevents Attacks
- ✅ Brute force login attempts
- ✅ DDoS attacks
- ✅ Spam bidding
- ✅ API abuse

### Ensures Fair Usage
- ✅ Equal access for all users
- ✅ Prevents one user from hogging resources
- ✅ Better performance for everyone

### Protects Your Server
- ✅ Prevents overload
- ✅ Maintains stability
- ✅ Reduces costs

---

## 📱 Frontend Implementation

### Handle 429 Errors

```javascript
async function login(email, password) {
    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        if (response.status === 429) {
            const data = await response.json();
            const retryAfter = response.headers.get('Retry-After');
            
            // Show user-friendly message
            alert(`Too many attempts. Please wait ${retryAfter} seconds.`);
            
            // Optional: Start countdown timer
            startCountdown(retryAfter);
            
            return;
        }
        
        const data = await response.json();
        // Handle successful login
        
    } catch (error) {
        console.error('Login error:', error);
    }
}
```

### Countdown Timer

```javascript
function startCountdown(seconds) {
    const button = document.getElementById('loginButton');
    button.disabled = true;
    
    const interval = setInterval(() => {
        seconds--;
        button.textContent = `Wait ${seconds}s`;
        
        if (seconds <= 0) {
            clearInterval(interval);
            button.disabled = false;
            button.textContent = 'Login';
        }
    }, 1000);
}
```

### Retry with Exponential Backoff

```javascript
async function loginWithRetry(email, password, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            
            if (response.status === 429) {
                const retryAfter = response.headers.get('Retry-After');
                await sleep(retryAfter * 1000);
                continue;
            }
            
            return await response.json();
            
        } catch (error) {
            if (i === maxRetries - 1) throw error;
            await sleep(Math.pow(2, i) * 1000); // Exponential backoff
        }
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
```

---

## 🔍 Monitoring Rate Limits

### Check Rate Limiter Stats

```python
from core.rate_limiter import rate_limiter

stats = rate_limiter.get_stats()
print(stats)
# {
#     "active_users": 45,
#     "active_ips": 38,
#     "active_bidders": 12,
#     "total_tracked_requests": 1250
# }
```

### Clear Specific IP

```python
from core.rate_limiter import rate_limiter

# Clear rate limits for specific IP
rate_limiter.clear_ip_limits("127.0.0.1")
```

### Clear All Limits

```python
from core.rate_limiter import rate_limiter

# Clear all rate limits (admin only)
rate_limiter.clear_all_limits()
```

---

## ⚙️ Configuration

### Environment Variables

```env
# Enable/Disable rate limiting
ENABLE_RATE_LIMITING=true

# For development, you might want to disable it
ENABLE_RATE_LIMITING=false
```

### Current Settings

```
Authentication: 10 attempts / 5 minutes
Bidding:        10 bids / 1 minute
General API:    100 requests / 1 minute
```

---

## 🚨 Troubleshooting

### Problem: Getting 429 on Every Login
**Solution**: 
1. Wait 5 minutes
2. Or restart server
3. Or disable rate limiting in .env

### Problem: Rate Limits Too Strict
**Solution**: 
1. Edit `core/rate_limiter.py`
2. Increase limits
3. Restart server

### Problem: Rate Limits Too Lenient
**Solution**: 
1. Edit `core/rate_limiter.py`
2. Decrease limits
3. Restart server

### Problem: Need to Clear Limits Immediately
**Solution**: 
```bash
# Restart server (fastest way)
# Stop with Ctrl+C
venv\Scripts\python main_new.py
```

---

## ✅ Summary

### Current Status
- ✅ Rate limiting: **ACTIVE**
- ✅ Authentication: **10 attempts / 5 min**
- ✅ Bidding: **10 bids / min**
- ✅ General API: **100 requests / min**

### Benefits
- ✅ Prevents brute force attacks
- ✅ Stops spam bidding
- ✅ Protects server resources
- ✅ Ensures fair usage

### Quick Fixes
- ✅ Wait 5 minutes (auto-expire)
- ✅ Restart server (clears all)
- ✅ Disable in .env (development)

---

**Status**: ✅ RATE LIMITING ACTIVE  
**Protection**: 🛡️ MAXIMUM  
**Performance**: ⚡ OPTIMIZED  
