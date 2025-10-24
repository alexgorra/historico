import java.io.*;
import java.net.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

public class GameServer {
    private static final int PORT = 5555;
    private static Map<String, Player> players = new ConcurrentHashMap<>();
    private static Map<String, Projectile> projectiles = new ConcurrentHashMap<>();
    private static List<ClientHandler> clients = new CopyOnWriteArrayList<>();
    private static int playerIdCounter = 0;
    private static int projectileIdCounter = 0;

    public static void main(String[] args) {
        System.out.println("Game Server started on port " + PORT);
        
        // Start projectile update thread
        Thread projectileThread = new Thread(GameServer::updateProjectiles);
        projectileThread.setDaemon(true);
        projectileThread.start();
        
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
        private static final int DEFAULT_MAX_HP = 100;

        Player(String id, int x, int y, String color) {
            this.id = id;
            this.x = x;
            this.y = y;
            this.color = color;
            this.maxHp = DEFAULT_MAX_HP;
            this.currentHp = DEFAULT_MAX_HP;
        }
        
        boolean takeDamage(int damage) {
            currentHp = Math.max(0, currentHp - damage);
            return currentHp > 0; // Returns true if still alive
        }
        
        void respawn(int newX, int newY) {
            this.x = newX;
            this.y = newY;
            this.currentHp = this.maxHp; // Restore to full health
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

                // Send welcome message with player info
                out.println("WELCOME:" + playerId + ":" + startX + ":" + startY + ":" + color);

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
            String[] parts = message.split(":");
            if (parts.length == 4) {
                String victimId = parts[1];
                String shooterId = parts[2];
                String projectileId = parts[3];
                
                Player victim = players.get(victimId);
                Projectile projectile = projectiles.get(projectileId);
                
                if (victim != null && projectile != null) {
                    // Apply damage to the victim
                    boolean stillAlive = victim.takeDamage(projectile.damage);
                    
                    System.out.println("Player " + victimId + " was hit by player " + shooterId + 
                                     " for " + projectile.damage + " damage. HP: " + 
                                     victim.currentHp + "/" + victim.maxHp);
                    
                    // Broadcast damage event to all clients
                    broadcastToAll("DAMAGE:" + victimId + ":" + victim.currentHp + ":" + victim.maxHp);
                    
                    // Check if player died and needs respawn
                    if (!stillAlive) {
                        System.out.println("Player " + victimId + " died! Respawning...");
                        
                        // Generate random respawn position
                        Random rand = new Random();
                        int respawnX = 100 + rand.nextInt(2200); // Random X within world bounds
                        int respawnY = 100 + rand.nextInt(1600); // Random Y within world bounds
                        
                        // Respawn the player
                        victim.respawn(respawnX, respawnY);
                        
                        // Broadcast respawn event to all clients
                        broadcastToAll("RESPAWN:" + victimId + ":" + respawnX + ":" + respawnY);
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