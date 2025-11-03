# Refract Minigame

A multiplayer top-down survival game with a Java server and Python (Pygame) client.

## Code Layout & Architecture

```
refract-minigame/
├── GameServer.java         # Java server: manages game state, players, enemies
├── run_server.sh           # Shell script to start the server
├── run_refactored_game.sh  # Shell script to start the Python client
├── assets/                 # Sprites, animations, and map data
├── game/
│   ├── main.py             # Main Pygame client entry point
│   ├── network_client.py   # Handles TCP communication with server
│   ├── game_renderer.py    # Handles all drawing and display logic
│   ├── animation_system.py # Animation and sprite management
│   ├── game_constants.py   # Shared constants/configuration
│   ├── map_system.py       # Map rendering and collision
│   ├── entities/           # Player, Enemy, Projectile, etc.
│   ├── systems/            # Component systems: movement, collision, health, render
│   └── core/               # Core ECS: GameObject, GameState, ComponentSystem
└── game_env/               # Python virtual environment (optional)
```

## Architecture
- **Server:** Java, authoritative, manages all game logic, player state, enemy spawning, and waves.
- **Client:** Python (Pygame), component-based, handles rendering, input, and local animation/interpolation.
- **Networking:** TCP, string-based protocol (e.g. `UPDATE:playerId:x:y`)
- **Assets:** Sprites and animations in `assets/` (Aseprite JSON/PNG)

## How to Run

### 1. Start the Server
```sh
cd refract-minigame
./run_server.sh
```

### 2. Start the Client (in a new terminal)
```sh
cd refract-minigame
./run_refactored_game.sh
```

- The client will connect to the server on `localhost:5555` by default.
- Multiple clients can be started for multiplayer.

### 3. Controls
- **WASD**: Move
- **Mouse**: Aim
- **Left Click**: Shoot
- **Space**: (Host only) Start game

---

- Make sure you have Java (for the server) and Python 3.12 + Pygame (for the client) installed.
- For best results, use the provided virtual environment in `game_env/`.
