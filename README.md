
# Minigame Project

## Project Structure

```
minigame-clean/
├── src/
│   ├── game_client.py
│   ├── game_constants.py
│   ├── game_renderer.py
│   ├── GameServer.java
│   ├── input_handler.py
│   ├── network_client.py
│   └── projectile_system.py
├── run_game.sh
├── run_server.sh
├── git_commit.sh
├── .gitignore
└── README.md
```

## How to Use

**Start the server:**
```bash
./run_server.sh
```

**Run the game client:**
```bash
./run_game.sh
```

**Commit and push changes (not tracked by git):**
```bash
./git_commit.sh "your commit message"
```

Scripts must be executable. If needed, run:
```bash
chmod +x *.sh
```