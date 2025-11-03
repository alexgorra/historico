import java.io.*;
import java.net.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

public class GameServer {
    private static final int PORT = 5555;
    private static Map<String, Player> players = new ConcurrentHashMap<>();
    private static Map<String, Projectile> projectiles = new ConcurrentHashMap<>();
    private static Map<String, Enemy> enemies = new ConcurrentHashMap<>();
    private static List<ClientHandler> clients = new CopyOnWriteArrayList<>();
    private static int playerIdCounter = -1; // Start at -1 so first player is player0
    private static int projectileIdCounter = 0;
    private static int enemyIdCounter = 0;
    
    // Game state
    private static GamePhase gamePhase = GamePhase.MENU;
    private static int currentWave = 0;
    private static long waveStartTime = 0;
    private static Set<String> deadPlayers = ConcurrentHashMap.newKeySet();
    private static String hostPlayerId = null; // Track the current host
    
    // Game constants
    private static final int ENEMIES_PER_WAVE = 5;
    private static final int WAVE_DELAY_MS = 10000; // 10 seconds
    private static final int ENEMY_UPDATE_INTERVAL_MS = 50; // 20 updates per second
    private static final int ENEMY_SPAWN_DELAY_MS = 5000; // 5 seconds after game start

    enum GamePhase {
        MENU, PLAYING, GAME_OVER
    }

    public static void main(String[] args) {
        System.out.println("Game Server started on port " + PORT);
        
        // Start projectile update thread
        Thread projectileThread = new Thread(GameServer::updateProjectiles);
        projectileThread.setDaemon(true);
        projectileThread.start();
        
        // Start enemy update thread
        Thread enemyThread = new Thread(GameServer::updateEnemies);
        enemyThread.setDaemon(true);
        enemyThread.start();
        
        // Start game logic thread
        Thread gameThread = new Thread(GameServer::updateGameLogic);
        gameThread.setDaemon(true);
        gameThread.start();
        
        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            while (true) {
                Socket clientSocket = serverSocket.accept();
                ClientHandler clientHandler = new ClientHandler(clientSocket);
                clients.add(clientHandler);
                clientHandler.start();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void updateProjectiles() {
        while (true) {
            try {
                List<String> toRemove = new ArrayList<>();
                
                // Update all projectiles and broadcast their new positions
                for (Map.Entry<String, Projectile> entry : projectiles.entrySet()) {
                    Projectile projectile = entry.getValue();
                    if (!projectile.update()) {
                        toRemove.add(entry.getKey());
                    } else {
                        // Broadcast updated position to all clients
                        broadcastToAll("PROJECTILE_UPDATE:" + projectile.id + ":" + 
                                     projectile.x + ":" + projectile.y + ":" + 
                                     projectile.directionX + ":" + projectile.directionY + ":" + 
                                     projectile.ownerId);
                    }
                }
                
                // Remove expired projectiles
                for (String projectileId : toRemove) {
                    projectiles.remove(projectileId);
                    broadcastToAll("PROJECTILE_REMOVE:" + projectileId);
                }
                
                Thread.sleep(16); // ~60 FPS
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
    
    private static void updateEnemies() {
        while (true) {
            try {
                if (gamePhase == GamePhase.PLAYING) {
                    List<String> toRemove = new ArrayList<>();
                    
                    // Update all enemies
                    for (Map.Entry<String, Enemy> entry : enemies.entrySet()) {
                        Enemy enemy = entry.getValue();
                        if (!enemy.active) {
                            toRemove.add(entry.getKey());
                            continue;
                        }
                        
                        // Update enemy AI and position
                        enemy.update(players);
                        
                        // Broadcast enemy state to all clients
                        broadcastToAll("ENEMY_UPDATE:" + enemy.id + ":" + enemy.x + ":" + enemy.y + ":" +
                                     enemy.currentHp + ":" + enemy.maxHp);
                        
                        // Check if enemy should damage player
                        enemy.checkDamagePlayer(players, deadPlayers);
                    }
                    
                    // Remove dead enemies
                    for (String enemyId : toRemove) {
                        enemies.remove(enemyId);
                    }
                }
                
                Thread.sleep(ENEMY_UPDATE_INTERVAL_MS);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
    
    private static void updateGameLogic() {
        while (true) {
            try {
                if (gamePhase == GamePhase.PLAYING) {
                    // Check if wave is complete (all enemies dead)
                    if (enemies.isEmpty() && System.currentTimeMillis() - waveStartTime > 2000) {
                        // Wave complete!
                        broadcastToAll("WAVE_COMPLETE:" + currentWave);
                        System.out.println("Wave " + currentWave + " complete!");
                        
                        // Respawn dead players
                        respawnDeadPlayers();
                        
                        // Check win condition (could add max waves here)
                        // For now, just continue spawning waves
                        
                        // Wait before spawning next wave
                        Thread.sleep(WAVE_DELAY_MS);
                        
                        // Spawn next wave
                        currentWave++;
                        spawnWave();
                    }
                    
                    // Check game over condition (all players dead)
                    int alivePlayers = players.size() - deadPlayers.size();
                    if (alivePlayers == 0 && !players.isEmpty()) {
                        gamePhase = GamePhase.GAME_OVER;
                        broadcastToAll("GAME_OVER:all_dead");
                        System.out.println("Game over - all players dead!");
                        
                        // Reset game state after delay
                        Thread.sleep(10000);
                        resetGame();
                    }
                }
                
                Thread.sleep(100); // Check game logic 10 times per second
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
    
    private static void spawnWave() {
        waveStartTime = System.currentTimeMillis();
        System.out.println("Spawning wave " + currentWave + " with " + ENEMIES_PER_WAVE + " enemies");
        
        Random rand = new Random();
        List<Player> playerList = new ArrayList<>(players.values());
        
        for (int i = 0; i < ENEMIES_PER_WAVE; i++) {
            // Pick random player to target
            if (playerList.isEmpty()) break;
            Player targetPlayer = playerList.get(rand.nextInt(playerList.size()));
            
            // Spawn enemy inside map bounds near edges
            int spawnX, spawnY;
            int side = rand.nextInt(4); // 0=top, 1=right, 2=bottom, 3=left
            int edgeMargin = 50; // Distance from edge to spawn
            
            switch (side) {
                case 0: // Top edge
                    spawnX = edgeMargin + rand.nextInt(2400 - edgeMargin * 2);
                    spawnY = edgeMargin;
                    break;
                case 1: // Right edge
                    spawnX = 2400 - edgeMargin;
                    spawnY = edgeMargin + rand.nextInt(1800 - edgeMargin * 2);
                    break;
                case 2: // Bottom edge
                    spawnX = edgeMargin + rand.nextInt(2400 - edgeMargin * 2);
                    spawnY = 1800 - edgeMargin;
                    break;
                default: // Left edge
                    spawnX = edgeMargin;
                    spawnY = edgeMargin + rand.nextInt(1800 - edgeMargin * 2);
                    break;
            }
            
            String enemyId = "enemy_" + (++enemyIdCounter);
            Enemy enemy = new Enemy(enemyId, spawnX, spawnY, targetPlayer.id);
            enemies.put(enemyId, enemy);
            
            // Broadcast enemy spawn to all clients
            broadcastToAll("ENEMY_SPAWN:" + enemyId + ":" + spawnX + ":" + spawnY + ":" + targetPlayer.id);
        }
    }
    
    private static void respawnDeadPlayers() {
        Random rand = new Random();
        for (String playerId : deadPlayers) {
            Player player = players.get(playerId);
            if (player != null) {
                int respawnX = 100 + rand.nextInt(2200);
                int respawnY = 100 + rand.nextInt(1600);
                player.respawn(respawnX, respawnY);
                broadcastToAll("RESPAWN:" + playerId + ":" + respawnX + ":" + respawnY);
                System.out.println("Respawned player " + playerId);
            }
        }
        deadPlayers.clear();
    }
    
    private static void resetGame() {
        gamePhase = GamePhase.MENU;
        currentWave = 0;
        enemies.clear();
        deadPlayers.clear();
        System.out.println("Game reset to menu");
    }

    private static void broadcastToAll(String message) {
        for (ClientHandler client : clients) {
            if (client.playerId != null && client.out != null) {
                try {
                    client.out.println(message);
                } catch (Exception e) {
                    System.out.println("Error broadcasting to " + client.playerId);
                }
            }
        }
    }

    static class Player {
        String id;
        int x, y;
        String color;
        int currentHp;
        int maxHp;
        boolean alive;
        private static final int DEFAULT_MAX_HP = 100;

        Player(String id, int x, int y, String color) {
            this.id = id;
            this.x = x;
            this.y = y;
            this.color = color;
            this.maxHp = DEFAULT_MAX_HP;
            this.currentHp = DEFAULT_MAX_HP;
            this.alive = true;
        }
        
        boolean takeDamage(int damage) {
            if (!alive) return false;
            currentHp = Math.max(0, currentHp - damage);
            if (currentHp == 0) {
                alive = false;
            }
            return currentHp > 0; // Returns true if still alive
        }
        
        void respawn(int newX, int newY) {
            this.x = newX;
            this.y = newY;
            this.currentHp = this.maxHp; // Restore to full health
            this.alive = true;
        }
    }

    static class Projectile {
        String id;
        double x, y;
        double directionX, directionY;
        String ownerId;
        long creationTime;
        int damage;
        private static final double SPEED = 8.0;
        private static final long LIFETIME = 5000;
        private static final int WORLD_WIDTH = 2400;
        private static final int WORLD_HEIGHT = 1800;
        private static final int DEFAULT_DAMAGE = 25; // 1/4 of max HP

        Projectile(String id, double x, double y, double directionX, double directionY, String ownerId) {
            this.id = id;
            this.x = x;
            this.y = y;
            this.directionX = directionX;
            this.directionY = directionY;
            this.ownerId = ownerId;
            this.creationTime = System.currentTimeMillis();
            this.damage = DEFAULT_DAMAGE;
        }

        boolean update() {
            x += directionX * SPEED;
            y += directionY * SPEED;
            
            if (x < 0 || x > WORLD_WIDTH || y < 0 || y > WORLD_HEIGHT || 
                (System.currentTimeMillis() - creationTime) > LIFETIME) {
                return false;
            }
            return true;
        }
    }
    
    static class Enemy {
        String id;
        double x, y;
        String targetPlayerId;
        int currentHp;
        int maxHp;
        boolean active;
        long lastDamageTime;
        private static final double SPEED = 1.0;
        private static final int DEFAULT_MAX_HP = 100;
        private static final int DAMAGE = 10;
        private static final int DAMAGE_RANGE = 46;
        private static final long DAMAGE_COOLDOWN_MS = 1000;
        private static final int STOP_DISTANCE = 30;
        
        Enemy(String id, double x, double y, String targetPlayerId) {
            this.id = id;
            this.x = x;
            this.y = y;
            this.targetPlayerId = targetPlayerId;
            this.maxHp = DEFAULT_MAX_HP;
            this.currentHp = DEFAULT_MAX_HP;
            this.active = true;
            this.lastDamageTime = 0;
        }
        
        void update(Map<String, Player> players) {
            // Find target player
            Player target = players.get(targetPlayerId);
            if (target == null || !target.alive) {
                // Target dead or gone, find new target
                for (Player p : players.values()) {
                    if (p.alive) {
                        target = p;
                        targetPlayerId = p.id;
                        break;
                    }
                }
            }
            
            if (target == null) return;
            
            // Calculate direction to target
            double dx = target.x - x;
            double dy = target.y - y;
            double distance = Math.sqrt(dx * dx + dy * dy);
            
            // Move towards target if not too close
            if (distance > STOP_DISTANCE) {
                x += (dx / distance) * SPEED;
                y += (dy / distance) * SPEED;
            }
        }
        
        void checkDamagePlayer(Map<String, Player> players, Set<String> deadPlayers) {
            Player target = players.get(targetPlayerId);
            if (target == null || !target.alive) return;
            
            // Check distance
            double dx = target.x - x;
            double dy = target.y - y;
            double distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance <= DAMAGE_RANGE) {
                // Check cooldown
                long currentTime = System.currentTimeMillis();
                if (currentTime - lastDamageTime >= DAMAGE_COOLDOWN_MS) {
                    boolean stillAlive = target.takeDamage(DAMAGE);
                    lastDamageTime = currentTime;
                    
                    System.out.println("Enemy " + id + " damaged player " + target.id + 
                                     " for " + DAMAGE + " damage. HP: " + target.currentHp + "/" + target.maxHp);
                    
                    // Broadcast damage
                    broadcastToAll("DAMAGE:" + target.id + ":" + target.currentHp + ":" + target.maxHp);
                    
                    if (!stillAlive) {
                        System.out.println("Player " + target.id + " killed by enemy!");
                        deadPlayers.add(target.id);
                        broadcastToAll("PLAYER_DEATH:" + target.id);
                    }
                }
            }
        }
        
        boolean takeDamage(int damage) {
            currentHp = Math.max(0, currentHp - damage);
            return currentHp > 0;
        }
    }

    static class ClientHandler extends Thread {
        private Socket socket;
        private PrintWriter out;
        private BufferedReader in;
        private String playerId;

        public ClientHandler(Socket socket) {
            this.socket = socket;
        }

        public void run() {
            try {
                in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                out = new PrintWriter(socket.getOutputStream(), true);

                // Generate unique player ID and random color
                playerId = "player_" + (++playerIdCounter);
                String color = generateRandomColor();
                
                // Create initial position
                Random rand = new Random();
                int startX = rand.nextInt(700);
                int startY = rand.nextInt(500);
                
                Player newPlayer = new Player(playerId, startX, startY, color);
                players.put(playerId, newPlayer);

                // Assign host if this is the first player
                boolean isHost = false;
                synchronized (GameServer.class) {
                    if (hostPlayerId == null) {
                        hostPlayerId = playerId;
                        isHost = true;
                        System.out.println("Player " + playerId + " is now the HOST");
                    }
                }

                // Send welcome message with player info and host status
                // Format: WELCOME:playerId:x:y:color:isHost
                out.println("WELCOME:" + playerId + ":" + startX + ":" + startY + ":" + color + ":" + isHost);

                // Send existing players to new client
                sendPlayerListToClient();

                // Broadcast new player to all other clients
                broadcastToOthers("NEW_PLAYER:" + playerId + ":" + startX + ":" + startY + ":" + color);

                System.out.println("Player " + playerId + " connected. Total players: " + players.size());

                // Handle client messages
                String message;
                while ((message = in.readLine()) != null) {
                    System.out.println("Received from " + playerId + ": " + message);
                    if (message.startsWith("MOVE:")) {
                        handleMove(message);
                    } else if (message.startsWith("SHOOT:")) {
                        handleShoot(message);
                    } else if (message.startsWith("HIT:")) {
                        handleHit(message);
                    } else if (message.startsWith("GAME_START:")) {
                        handleGameStart(message);
                    } else if (message.equals("DISCONNECT")) {
                        break;
                    }
                }
            } catch (IOException e) {
                System.out.println("Error handling client " + playerId + ": " + e.getMessage());
            } finally {
                disconnect();
            }
        }
        
        private void handleGameStart(String message) {
            // Format: GAME_START:playerId
            // Only the designated host can start the game
            if (playerId.equals(hostPlayerId) && gamePhase == GamePhase.MENU) {
                System.out.println("Host (" + playerId + ") starting game!");
                gamePhase = GamePhase.PLAYING;
                currentWave = 1;
                deadPlayers.clear();
                
                // Broadcast game start to all clients
                broadcastToAll("GAME_START");
                
                // Spawn first wave after 5 second delay
                new Thread(() -> {
                    try {
                        Thread.sleep(ENEMY_SPAWN_DELAY_MS);
                        spawnWave();
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }).start();
            }
        }

        private void handleMove(String message) {
            // Format: MOVE:playerId:x:y
            String[] parts = message.split(":");
            if (parts.length == 4) {
                String pid = parts[1];
                try {
                    int x = Integer.parseInt(parts[2]);
                    int y = Integer.parseInt(parts[3]);
                    
                    Player player = players.get(pid);
                    if (player != null) {
                        player.x = x;
                        player.y = y;
                        broadcast("UPDATE:" + pid + ":" + x + ":" + y);
                    }
                } catch (NumberFormatException e) {
                    System.out.println("Invalid move coordinates from " + playerId);
                }
            }
        }

        private void handleShoot(String message) {
            // Format: SHOOT:playerId:startX:startY:directionX:directionY
            String[] parts = message.split(":");
            if (parts.length == 6) {
                String pid = parts[1];
                try {
                    double startX = Double.parseDouble(parts[2]);
                    double startY = Double.parseDouble(parts[3]);
                    double directionX = Double.parseDouble(parts[4]);
                    double directionY = Double.parseDouble(parts[5]);
                    
                    // Create projectile
                    String projectileId = pid + "_" + (++projectileIdCounter);
                    Projectile projectile = new Projectile(projectileId, startX, startY, 
                                                          directionX, directionY, pid);
                    projectiles.put(projectileId, projectile);
                    
                    // Broadcast projectile to all clients
                    broadcast("PROJECTILE_UPDATE:" + projectileId + ":" + startX + ":" + startY + 
                             ":" + directionX + ":" + directionY + ":" + pid);
                    
                } catch (NumberFormatException e) {
                    System.out.println("Invalid shoot coordinates from " + playerId);
                }
            }
        }

        private void handleHit(String message) {
            // Format: HIT:victimId:shooterId:projectileId
            // victimId can be a playerId or enemyId
            String[] parts = message.split(":");
            if (parts.length == 4) {
                String victimId = parts[1];
                String shooterId = parts[2];
                String projectileId = parts[3];
                
                Projectile projectile = projectiles.get(projectileId);
                if (projectile == null) return;
                
                // Check if victim is a player
                Player victimPlayer = players.get(victimId);
                if (victimPlayer != null) {
                    // Apply damage to the player victim
                    boolean stillAlive = victimPlayer.takeDamage(projectile.damage);
                    
                    System.out.println("Player " + victimId + " was hit by player " + shooterId + 
                                     " for " + projectile.damage + " damage. HP: " + 
                                     victimPlayer.currentHp + "/" + victimPlayer.maxHp);
                    
                    // Broadcast damage event to all clients
                    broadcastToAll("DAMAGE:" + victimId + ":" + victimPlayer.currentHp + ":" + victimPlayer.maxHp);
                    
                    // Check if player died
                    if (!stillAlive) {
                        System.out.println("Player " + victimId + " was killed!");
                        deadPlayers.add(victimId);
                        broadcastToAll("PLAYER_DEATH:" + victimId);
                    }
                }
                
                // Check if victim is an enemy
                Enemy victimEnemy = enemies.get(victimId);
                if (victimEnemy != null) {
                    // Apply damage to the enemy
                    boolean stillAlive = victimEnemy.takeDamage(projectile.damage);
                    
                    System.out.println("Enemy " + victimId + " was hit by player " + shooterId + 
                                     " for " + projectile.damage + " damage. HP: " + 
                                     victimEnemy.currentHp + "/" + victimEnemy.maxHp);
                    
                    // Broadcast enemy update
                    broadcastToAll("ENEMY_UPDATE:" + victimEnemy.id + ":" + victimEnemy.x + ":" + victimEnemy.y + ":" +
                                 victimEnemy.currentHp + ":" + victimEnemy.maxHp);
                    
                    // Check if enemy died
                    if (!stillAlive) {
                        System.out.println("Enemy " + victimId + " was killed by player " + shooterId + "!");
                        victimEnemy.active = false;
                        broadcastToAll("ENEMY_DEATH:" + victimId + ":" + shooterId);
                    }
                }
                
                // Remove the projectile from server state
                if (projectiles.containsKey(projectileId)) {
                    projectiles.remove(projectileId);
                    // Broadcast projectile removal to all clients
                    broadcastToAll("PROJECTILE_REMOVE:" + projectileId);
                }
            }
        }

        private void sendPlayerListToClient() {
            StringBuilder sb = new StringBuilder("PLAYERS:");
            for (Player player : players.values()) {
                if (!player.id.equals(this.playerId)) { // Don't send self
                    sb.append(player.id).append(",")
                      .append(player.x).append(",")
                      .append(player.y).append(",")
                      .append(player.color).append(";");
                }
            }
            out.println(sb.toString());
        }

        private void broadcast(String message) {
            for (ClientHandler client : clients) {
                if (client.playerId != null && client.out != null) {
                    try {
                        client.out.println(message);
                    } catch (Exception e) {
                        System.out.println("Error broadcasting to " + client.playerId);
                    }
                }
            }
        }

        private void broadcastToOthers(String message) {
            for (ClientHandler client : clients) {
                if (client.playerId != null && !client.playerId.equals(this.playerId) && client.out != null) {
                    try {
                        client.out.println(message);
                    } catch (Exception e) {
                        System.out.println("Error broadcasting to " + client.playerId);
                    }
                }
            }
        }

        private String generateRandomColor() {
            String[] colors = {"red", "blue", "green", "yellow", "purple", "orange"};
            Random rand = new Random();
            return colors[rand.nextInt(colors.length)];
        }

        private void disconnect() {
            if (playerId != null) {
                players.remove(playerId);
                clients.remove(this);
                
                // Check if host is leaving and reassign if needed
                synchronized (GameServer.class) {
                    if (playerId.equals(hostPlayerId)) {
                        hostPlayerId = null;
                        System.out.println("Host " + playerId + " disconnected. Looking for new host...");
                        
                        // Assign new host from remaining players
                        if (!players.isEmpty()) {
                            // Get first available player as new host
                            String newHostId = players.keySet().iterator().next();
                            hostPlayerId = newHostId;
                            System.out.println("New host assigned: " + hostPlayerId);
                            
                            // Notify the new host
                            for (ClientHandler client : clients) {
                                if (client.playerId != null && client.playerId.equals(newHostId)) {
                                    client.out.println("HOST_ASSIGNED");
                                    break;
                                }
                            }
                        }
                    }
                }
                
                // Remove all projectiles owned by this player
                List<String> toRemove = new ArrayList<>();
                for (Map.Entry<String, Projectile> entry : projectiles.entrySet()) {
                    if (entry.getValue().ownerId.equals(playerId)) {
                        toRemove.add(entry.getKey());
                    }
                }
                for (String projectileId : toRemove) {
                    projectiles.remove(projectileId);
                    broadcastToAll("PROJECTILE_REMOVE:" + projectileId);
                }
                
                System.out.println("Player " + playerId + " disconnected. Total players: " + players.size());
                broadcast("PLAYER_LEFT:" + playerId);
            }
            try {
                if (socket != null) socket.close();
            } catch (IOException e) {
                System.out.println("Error closing socket for " + playerId);
            }
        }
    }
}