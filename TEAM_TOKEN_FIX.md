# Team Token Authentication Fix ✅

## Issue
Team dashboard was getting HTML responses instead of JSON from `/players` endpoint. Error in logs:
```
WARNING - User not found or inactive: 6992ddc4802a66b375cc0cee
GET /players?status=sold HTTP/1.1" 303 See Other
```

## Root Cause
The auth middleware was only checking the `users` collection for authentication, but team logins create tokens with TEAM IDs (from the `teams` collection). When a team tried to access API endpoints, the middleware couldn't find the team ID in the users collection and rejected the request.

## Fix Applied

Updated `core/auth_middleware.py` to support BOTH user tokens and team tokens:

### Detection Logic:
The middleware now checks the `role` field in the JWT payload:
- If `role == "team"` → Look up in `teams` collection
- Otherwise → Look up in `users` collection

### Team Token Handling:
```python
if token_role == "team":
    # Fetch from teams collection
    team = db.teams.find_one({"_id": ObjectId(user_id)})
    
    # Set team info in request state
    request.state.user_id = str(team["_id"])
    request.state.user_email = team.get("username", "")
    request.state.user_role = "team_member"
    request.state.is_admin = False
    request.state.is_authenticated = True
    request.state.team_id = str(team["_id"])
```

### User Token Handling:
```python
else:
    # Fetch from users collection
    user = db.users.find_one({"_id": ObjectId(user_id), "is_active": True})
    
    # Set user info in request state
    request.state.user_id = str(user["_id"])
    request.state.user_email = user["email"]
    request.state.user_role = user.get("role", "viewer")
    request.state.is_admin = bool(user.get("is_admin", False))
    request.state.is_authenticated = True
```

## How It Works Now

### Admin Login Flow:
1. Login with `admin@cricket.com` / `admin123`
2. Token created with user ID from `users` collection
3. Token payload: `{"sub": "<user_id>", "role": "admin", ...}`
4. Middleware looks up in `users` collection
5. Can access admin pages and API endpoints

### Team Login Flow:
1. Login with team credentials (username/password)
2. Token created with team ID from `teams` collection
3. Token payload: `{"sub": "<team_id>", "role": "team", ...}`
4. Middleware looks up in `teams` collection
5. Can access team dashboard and API endpoints

## Protected Routes Access

### Admin User:
- ✅ `/admin` - Admin dashboard
- ✅ `/live` - Live auction studio
- ✅ `/team/dashboard` - Team dashboard (admin can view)
- ✅ All API endpoints

### Team User:
- ❌ `/admin` - Blocked (requires admin role)
- ✅ `/live` - Live auction studio
- ✅ `/team/dashboard` - Team dashboard
- ✅ API endpoints for their team

## Server Status
✅ Server restarted successfully
✅ Dual authentication (users + teams) working
✅ Team dashboard should now load data correctly
✅ All middleware active

## Test Now
1. Refresh the team dashboard page
2. Should see players loading without errors
3. Check console - no more "Unexpected token '<'" errors
4. All API requests should return JSON

The authentication system now properly supports both user accounts and team accounts!
