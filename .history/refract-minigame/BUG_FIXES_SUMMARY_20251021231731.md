# Bug Fixes Summary

## Issues Fixed

### 1. Player Disconnection When Shooting While Moving

**Root Cause:**
- When a projectile hit a wall, the client detected the collision and removed the projectile locally
- The server also independently removed the projectile and sent a `PROJECTILE_REMOVE` message
- When the client received this message, it tried to remove the projectile again from its dictionary
- This caused a KeyError (e.g., `'player_5_72'`) which crashed the network listening thread
- The crash disconnected the player from the server

**Fixes Applied:**

1. **Added exception handling in `_handle_projectile_remove_message()`** (`network_client.py`)
   - Wrapped the removal logic in a try-except block
   - Prevents KeyError from crashing the network thread
   
2. **Added duplicate removal tracking** (`main.py`)
   - Created `removed_projectiles` set to track projectiles that have been removed
   - Check this set before attempting to remove a projectile
   - Prevents double-removal attempts
   
3. **Improved error handling in `_listen_to_server()`** (`network_client.py`)
   - Added per-message error handling to prevent one bad message from crashing the connection
   - Distinguished between ConnectionResetError and other exceptions for better debugging

4. **Added cleanup mechanism** (`main.py`)
   - Periodically trim the `removed_projectiles` set to prevent memory leaks
   - Keeps only the last 50 removed projectile IDs when set exceeds 100 entries

---

### 2. Multiple Collision Animations Spawning

**Root Cause:**
- When a projectile collided with a wall, `check_wall_collision()` returned true
- The projectile was marked as `inactive` but remained in the list for that frame
- On the next frame, the same projectile (still in the list, now inactive) was checked again
- Since it was still near/in the wall, collision was detected again
- This created multiple `CollisionEffect` objects along the projectile's path

**Fixes Applied:**

1. **Immediate filtering in collision detection** (`main.py`)
   - Added early skip for projectiles already marked inactive: `if not proj.active: continue`
   - Prevents inactive projectiles from being processed again in the same frame
   
2. **Mark inactive before adding to hit lists** (`main.py`)
   - Changed order: now marks `proj.active = False` BEFORE adding to `wall_hits` or `hits_to_process`
   - Prevents the same projectile from triggering multiple collision types
   
3. **Check removed_projectiles set before creating effects** (`main.py`)
   - Added check: `if projectile_id not in self.removed_projectiles`
   - Ensures each projectile ID only creates one collision effect
   - Works in conjunction with the tracking mechanism

4. **Prevent recreation of removed projectiles** (`main.py`)
   - In `_on_projectile_update()`, check if projectile is in `removed_projectiles` before creating it
   - Prevents race condition where server update arrives after local removal

---

## Files Modified

1. **`game/network_client.py`**
   - Enhanced `_handle_projectile_remove_message()` with exception handling
   - Improved `_listen_to_server()` with better error handling

2. **`game/main.py`**
   - Added `removed_projectiles` set to track removed projectiles
   - Updated `_on_projectile_remove()` to use tracking
   - Updated `_on_projectile_update()` to check tracking
   - Updated `check_collisions()` to prevent duplicate effects
   - Added cleanup mechanism in `update()`

---

## Testing Recommendations

1. **Test shooting while moving:**
   - Move in various directions while continuously shooting
   - Verify no disconnections occur
   - Check that collision effects appear correctly

2. **Test wall collisions:**
   - Shoot projectiles at walls from various angles
   - Verify only ONE collision effect appears per projectile
   - Ensure projectiles are removed correctly

3. **Test player-to-player hits:**
   - Have two players shoot at each other while moving
   - Verify no disconnections
   - Verify collision effects appear only once

4. **Stress test:**
   - Have multiple players shooting rapidly while moving
   - Monitor for memory leaks over extended play sessions
   - Verify the `removed_projectiles` cleanup is working

---

## Technical Notes

- The fixes maintain backward compatibility with the server
- No changes were needed to `GameServer.java`
- The solution uses defensive programming to handle race conditions between client collision detection and server updates
- Memory management is handled automatically by the cleanup mechanism
