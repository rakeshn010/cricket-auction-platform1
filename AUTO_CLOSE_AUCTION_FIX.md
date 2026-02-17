# Auto-Close Auction After Timer Expires

## Problem
After the 30-second timer expires, teams can still place bids. The auction should automatically close when time runs out.

## Solution Applied

### 1. Auto-Close Callback
When a player is set live, the timer now includes an auto-close callback that:
- Automatically closes the auction when timer reaches 0
- Marks player as SOLD if there are bids
- Marks player as UNSOLD if there are no bids
- Updates team budgets and player counts
- Broadcasts the result to all clients
- Clears the current player from auction config

### 2. Prevent Bids After Timer Expires
Updated `services/bid_service.py` to check timer status:
```python
# Check if timer is still running (prevent bids after timer expires)
if not manager.timer_running or manager.timer_seconds <= 0:
    raise HTTPException(
        status_code=400, 
        detail="Auction time has expired. Please wait for admin to set next player."
    )
```

### 3. Disable Bid Button in UI
Updated `static/team_dashboard_new.js`:
- Bid button is enabled when timer > 0
- Bid button is disabled when timer = 0
- Button text changes to "Auction Closed"
- Toast notification shows "Time expired! Auction is being finalized..."

## How It Works

### Normal Flow:
1. Admin sets player live → Timer starts at 30 seconds
2. Teams can bid while timer > 0
3. Each bid resets timer to 30 seconds
4. Timer counts down: 30, 29, 28... 3, 2, 1, 0

### When Timer Reaches 0:

#### If Player Has Bids:
1. Player automatically marked as SOLD
2. Highest bidding team gets the player
3. Team's budget updated (deducted)
4. Team's player count incremented
5. Broadcast "player_sold" event
6. Bid button disabled
7. Admin can set next player

#### If Player Has No Bids:
1. Player automatically marked as UNSOLD
2. No budget changes
3. Broadcast "player_unsold" event
4. Bid button disabled
5. Admin can set next player

### Bid Attempts After Timer Expires:
- Backend rejects with error: "Auction time has expired"
- Frontend shows disabled button
- Toast notification explains auction is closed

## Benefits

1. **Fair Auction**: No bids accepted after time expires
2. **Automatic Processing**: Admin doesn't need to manually close each auction
3. **Clear Feedback**: Users see when bidding is closed
4. **Prevents Confusion**: Button disabled = no more bids
5. **Faster Auction**: Automatic closure speeds up the process

## Testing

### Test Auto-Close with Bids:
1. Set a player live
2. Place at least one bid
3. Wait for timer to reach 0
4. Player should automatically be marked SOLD
5. Bid button should be disabled
6. Toast should show "Auction Closed"

### Test Auto-Close without Bids:
1. Set a player live
2. Don't place any bids
3. Wait for timer to reach 0
4. Player should automatically be marked UNSOLD
5. Bid button should be disabled

### Test Bid Prevention:
1. Set a player live
2. Wait for timer to reach 0
3. Try to place a bid
4. Should see error: "Auction time has expired"
5. Button should be disabled

## Files Modified

1. `routers/admin.py`
   - Added `auto_close_auction()` callback function
   - Passes callback to `manager.start_timer()`

2. `services/bid_service.py`
   - Added timer check before accepting bids
   - Rejects bids when timer expired

3. `static/team_dashboard_new.js`
   - Disables bid button when timer = 0
   - Shows "Auction Closed" message
   - Displays toast notification

## Expected Behavior

✅ Timer counts down from 30 seconds  
✅ Bids reset timer to 30 seconds  
✅ When timer reaches 0:
  - Auction automatically closes
  - Player marked SOLD or UNSOLD
  - Bid button disabled
  - No more bids accepted
  - Admin can set next player

This ensures a fair, time-bound auction process!
