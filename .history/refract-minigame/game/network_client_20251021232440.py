"""
Network client module for handling server communication in the multiplayer game.
"""

import socket
import threading
import traceback
from game_constants import *


class NetworkClient:
    def __init__(self, host=DEFAULT_SERVER_HOST, port=DEFAULT_SERVER_PORT):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        
        # Player data received from server
        self.player_id = None
        self.player_x = 0
        self.player_y = 0
        self.player_color = None
        
        # Other players data
        self.other_players = {}
        
        # Message buffer for handling TCP stream fragmentation
        self.message_buffer = ""
        
        # Callback functions for handling events
        self.on_welcome = None
        self.on_player_update = None
        self.on_new_player = None
        self.on_player_left = None
        self.on_disconnect = None
        self.on_projectile_update = None
        self.on_projectile_remove = None
        
    def set_callbacks(self, on_welcome=None, on_player_update=None, 
                     on_new_player=None, on_player_left=None, on_disconnect=None,
                     on_projectile_update=None, on_projectile_remove=None):
        """Set callback functions for network events."""
        self.on_welcome = on_welcome
        self.on_player_update = on_player_update
        self.on_new_player = on_new_player
        self.on_player_left = on_player_left
        self.on_disconnect = on_disconnect
        self.on_projectile_update = on_projectile_update
        self.on_projectile_remove = on_projectile_remove
        
    def connect(self):
        """Connect to the game server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            
            # Start listening thread
            listen_thread = threading.Thread(target=self._listen_to_server)
            listen_thread.daemon = True
            listen_thread.start()
            
            print("Connected to server successfully!")
            return True
            
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the server."""
        if self.connected:
            try:
                self.send_message(MSG_DISCONNECT)
                self.socket.close()
            except:
                pass
            self.connected = False
            if self.on_disconnect:
                self.on_disconnect()
    
    def send_move(self, x, y):
        """Send player movement to server."""
        if self.connected and self.player_id:
            message = f"{MSG_MOVE}:{self.player_id}:{x}:{y}"
            self.send_message(message)
    
    def send_shoot(self, start_x, start_y, direction_x, direction_y):
        """Send projectile shooting to server."""
        if self.connected and self.player_id:
            message = f"{MSG_SHOOT}:{self.player_id}:{start_x}:{start_y}:{direction_x}:{direction_y}"
            self.send_message(message)
    
    def send_hit(self, victim_id, shooter_id, projectile_id):
        """Send hit notification to server."""
        if self.connected and self.player_id:
            message = f"{MSG_HIT}:{victim_id}:{shooter_id}:{projectile_id}"
            self.send_message(message)
    
    def send_message(self, message):
        """Send a message to the server."""
        if self.connected:
            try:
                self.socket.send((message + '\n').encode('utf-8'))
            except Exception as e:
                print(f"Error sending message: {e}")
                self.connected = False
    
    def _listen_to_server(self):
        """Listen for messages from the server (runs in separate thread)."""
        while self.connected:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                # Add received data to buffer
                self.message_buffer += data
                
                # Process complete messages (terminated by '\n')
                while '\n' in self.message_buffer:
                    # Find the first newline
                    newline_pos = self.message_buffer.index('\n')
                    # Extract the complete message
                    message = self.message_buffer[:newline_pos].strip()
                    # Remove processed message from buffer
                    self.message_buffer = self.message_buffer[newline_pos + 1:]
                    
                    # Process the complete message
                    if message:
                        try:
                            self._handle_server_message(message)
                        except Exception as msg_error:
                            # Log but don't crash on message handling errors
                            print(f"Error handling message '{message}': {msg_error}")
                
                # Prevent buffer from growing too large (safety limit)
                if len(self.message_buffer) > 10000:
                    print("Warning: Message buffer overflow, clearing partial message")
                    self.message_buffer = ""
                
            except ConnectionResetError:
                print("Connection reset by server")
                break
            except UnicodeDecodeError as e:
                print(f"Error decoding message: {e}")
                # Clear buffer and continue
                self.message_buffer = ""
                continue
            except Exception as e:
                print(f"Error receiving data: {e}")
                break
        
        self.connected = False
        print("Disconnected from server")
        if self.on_disconnect:
            self.on_disconnect()
    
    def _handle_server_message(self, message):
        """Handle incoming message from server."""
        print(f"Received: {message}")  # Debug print
        
        try:
            if message.startswith(f"{MSG_WELCOME}:"):
                self._handle_welcome_message(message)
            elif message.startswith(f"{MSG_PLAYERS}:"):
                self._handle_players_message(message)
            elif message.startswith(f"{MSG_UPDATE}:"):
                self._handle_update_message(message)
            elif message.startswith(f"{MSG_NEW_PLAYER}:"):
                self._handle_new_player_message(message)
            elif message.startswith(f"{MSG_PLAYER_LEFT}:"):
                self._handle_player_left_message(message)
            elif message.startswith(f"{MSG_PROJECTILE_UPDATE}:"):
                self._handle_projectile_update_message(message)
            elif message.startswith(f"{MSG_PROJECTILE_REMOVE}:"):
                self._handle_projectile_remove_message(message)
            else:
                print(f"Warning: Unknown message type: {message[:50]}")
        except Exception as e:
            print(f"Error in message handler for '{message[:50]}...': {e}")
            import traceback
            traceback.print_exc()
    
    def _handle_welcome_message(self, message):
        """Handle welcome message from server."""
        # Format: WELCOME:playerId:x:y:color
        parts = message.split(":")
        if len(parts) >= 5:
            self.player_id = parts[1]
            self.player_x = int(parts[2])
            self.player_y = int(parts[3])
            self.player_color = parts[4]
            print(f"Welcome! You are {self.player_id} with color {self.player_color}")
            if self.on_welcome:
                self.on_welcome(self.player_id, self.player_x, self.player_y, self.player_color)
    
    def _handle_players_message(self, message):
        """Handle players list message from server."""
        # Format: PLAYERS:player1,x1,y1,color1;player2,x2,y2,color2;...
        players_data = message[len(f"{MSG_PLAYERS}:"):]  # Remove "PLAYERS:"
        self.other_players.clear()
        
        if players_data:
            player_entries = players_data.split(";")
            
            for entry in player_entries:
                if entry and "," in entry:
                    player_parts = entry.split(",")
                    if len(player_parts) >= 4:
                        pid, x, y, color = player_parts
                        if pid != self.player_id:
                            self.other_players[pid] = {
                                'x': int(x),
                                'y': int(y),
                                'color': color
                            }
        
        print(f"Updated player list: {list(self.other_players.keys())}")
        if self.on_player_update:
            self.on_player_update(self.other_players)
    
    def _handle_update_message(self, message):
        """Handle player position update message."""
        # Format: UPDATE:playerId:x:y
        parts = message.split(":")
        if len(parts) >= 4:
            pid, x, y = parts[1], parts[2], parts[3]
            if pid in self.other_players:
                self.other_players[pid]['x'] = int(x)
                self.other_players[pid]['y'] = int(y)
                if self.on_player_update:
                    self.on_player_update(self.other_players)
    
    def _handle_new_player_message(self, message):
        """Handle new player joined message."""
        # Format: NEW_PLAYER:playerId:x:y:color
        parts = message.split(":")
        if len(parts) >= 5:
            pid, x, y, color = parts[1], parts[2], parts[3], parts[4]
            if pid != self.player_id:
                self.other_players[pid] = {
                    'x': int(x),
                    'y': int(y),
                    'color': color
                }
                print(f"New player joined: {pid}")
                if self.on_new_player:
                    self.on_new_player(pid, x, y, color)
                if self.on_player_update:
                    self.on_player_update(self.other_players)
    
    def _handle_player_left_message(self, message):
        """Handle player left message."""
        # Format: PLAYER_LEFT:playerId
        pid = message.split(":")[1]
        if pid in self.other_players:
            del self.other_players[pid]
            print(f"Player left: {pid}")
            if self.on_player_left:
                self.on_player_left(pid)
            if self.on_player_update:
                self.on_player_update(self.other_players)
    
    def _handle_projectile_update_message(self, message):
        """Handle projectile update message."""
        # Format: PROJECTILE_UPDATE:projectileId:x:y:directionX:directionY:ownerId
        parts = message.split(":")
        if len(parts) >= 7:
            projectile_data = {
                'id': parts[1],
                'x': float(parts[2]),
                'y': float(parts[3]),
                'direction_x': float(parts[4]),
                'direction_y': float(parts[5]),
                'owner_id': parts[6]
            }
            if self.on_projectile_update:
                self.on_projectile_update(projectile_data)
    
    def _handle_projectile_remove_message(self, message):
        """Handle projectile removal message."""
        # Format: PROJECTILE_REMOVE:projectileId
        try:
            parts = message.split(":")
            if len(parts) >= 2:
                projectile_id = parts[1]
                if self.on_projectile_remove:
                    self.on_projectile_remove(projectile_id)
        except Exception as e:
            # Silently handle projectile removal errors (projectile may already be removed)
            print(f"Warning: Could not remove projectile from message '{message}': {e}")
    
    def get_player_count(self):
        """Get total number of players (including self)."""
        return len(self.other_players) + (1 if self.player_id else 0)
