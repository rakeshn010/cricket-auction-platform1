# Player Image Fallback Fix

## Problem
Player images were showing 404 errors when the image files didn't exist on the server, causing console errors and broken image icons.

## Solution
Added automatic fallback handling for missing player images across all pages:

### 1. Admin Panel (`static/admin.js`)
- **Pending Approvals**: Added `onerror` handler that displays an SVG placeholder with the player's first initial
- **Player Cards**: Already had emoji placeholder (👤), enhanced with proper error handling
- **Unsold Players**: Added `onerror` handler that replaces broken images with a styled div showing the first letter

### 2. Team Dashboard (`static/team_dashboard_new.js`)
- Added `onerror` handler that replaces broken images with the existing placeholder icon
- Maintains consistent UI even when images fail to load

### 3. How It Works
When an image fails to load (404 error):
1. The `onerror` event fires automatically
2. The handler replaces the broken image with a fallback:
   - Admin panel: Gray box with player's first initial or emoji
   - Team dashboard: Icon placeholder
3. The `onerror=null` prevents infinite loops if the fallback also fails

## Benefits
- No more 404 errors in console for missing images
- Consistent user experience regardless of image availability
- Automatic handling - no manual intervention needed
- Works for both existing and future players

## Example Fallbacks
- **Admin Panel**: Shows "V" for player named "Venu" in a styled box
- **Team Dashboard**: Shows person icon placeholder
- **Pending Approvals**: Shows SVG with player's initial

## Files Modified
- `static/admin.js` - Added onerror handlers to 3 image rendering locations
- `static/team_dashboard_new.js` - Added onerror handler to player image rendering

## Testing
After deployment:
1. Players with missing images will show placeholders instead of broken icons
2. No 404 errors will appear in the browser console for player images
3. UI remains clean and professional even with missing images

## Future Prevention
This fix ensures that:
- New players without images will show placeholders automatically
- Deleted images won't break the UI
- Image upload failures are handled gracefully
- The system is resilient to file system issues
