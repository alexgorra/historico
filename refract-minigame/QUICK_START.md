# Multiplayer Wave Survival Game - Quick Start Guide

## Prerequisites
- Java JDK (for server)
- Python 3.12+ (for client)
- Pygame 2.6.1+ (install via `pip install pygame`)

## Starting the Game

### 1. Start the Server
```bash
# From the refract-minigame directory
javac GameServer.java
java GameServer
```

The server will start on port 5555 and display:
```
Game Server started on port 5555
```

### 2. Start Client(s)
```bash
# Terminal 1 (Player 1 - Host)
cd game
python3 main.py
```

```bash
# Terminal 2 (Player 2)
cd game
python3 main.py
```

```bash
# Terminal 3 (Player 3)
cd game  
python3 main.py
```

## How to Play

### Menu Phase
1. **First player (player0)** connects and sees:
   - "You are the HOST"
   - "Press SPACE to start the game"
   
2. **Other players** connect and see:
   - "Waiting for host to start..."
   - Player count updates in real-time

3. **Host** presses **SPACE** to start the game

### Playing Phase
- **Movement**: WASD or Arrow Keys
- **Shoot**: Left Mouse Click (aim with mouse)
- **Objective**: Survive waves of enemies

#### Wave System
- Each wave spawns 5 enemies
- Enemies target the nearest player
- Kill all enemies to complete the wave
- 10-second delay before next wave

#### Combat
- **Player Health**: 100 HP
- **Projectile Damage**: 25 HP (4 hits to kill)
- **Enemy Health**: 100 HP  
- **Enemy Damage**: 10 HP per hit (1 second cooldown)

### Death Phase
If you die:
- See "YOU DIED" screen overlay
- Game world still visible
- Shows alive player count (e.g., "Alive: 2/4")
- Wait for current wave to complete
- **Respawn with all other dead players** when wave ends

### Game Over
- **All players dead**: Game over screen appears
- **Solo play**: Death = immediate game over
- Shows final kill count
- Server resets to menu after 10 seconds

## UI Elements

### Top Left
- Connection status
- Player count

### Top Right  
- Kill count
- Wave number (during gameplay)

### Health Bars
- Green bars above players and enemies
- Shows current HP / max HP

## Multiplayer Features

✅ **Synchronized Enemies**: All players see same enemies  
✅ **Shared Waves**: Team completes waves together  
✅ **Group Respawn**: Dead players respawn together  
✅ **Kill Tracking**: Individual kill counts  
✅ **Real-time Updates**: 60 FPS game, 20 FPS enemy updates  

## Troubleshooting

### "Connection failed"
- Make sure server is running first
- Check firewall settings for port 5555

### Enemies not appearing
- Wait for host to press SPACE in menu
- Check server console for "Spawning wave..." message

### Collision issues
- Enemies use collision avoidance
- Players have priority in collisions
- Restart client if objects get stuck

## Game Configuration

Edit `game/game_constants.py` for:
- Screen resolution (WIDTH, HEIGHT)
- Player speed, health
- Projectile settings
- Enemy settings (speed, damage, health)

Edit `GameServer.java` for:
- Enemies per wave (ENEMIES_PER_WAVE)
- Wave delay (WAVE_DELAY_MS)
- Server port (PORT)

## Tips for Playing

1. **Solo Play**: Challenging! One death = game over
2. **2-4 Players**: Optimal teamwork experience
3. **Communication**: Coordinate who targets which enemy
4. **Positioning**: Don't let enemies surround you
5. **Revive Strategy**: Protect alive players during respawn wait
6. **Kiting**: Move while shooting to avoid damage

## Development

### Run Scripts
```bash
# Start server
./run_server.sh

# Start client (activate virtual env first)
./run_refactored_game.sh
```

### Debug Mode
- Set `DRAW_HITBOXES = True` in `game_constants.py` to see collision boxes

## Credits

Built with:
- **Pygame** for rendering and input
- **Java** for server-side game logic
- **TCP sockets** for networking
- **Aseprite animations** for sprites

Enjoy the game! 🎮
