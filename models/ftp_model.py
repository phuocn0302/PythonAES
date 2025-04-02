# ftpserver.py
import os
import socket
import threading
import time
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

class FTPServerManager:
    def __init__(self):
        self.server = None
        self.server_thread = None
        self.running = False
        self.status_callback = None
        self.log_callback = None
        
        self.host = "127.0.0.1"
        self.port = 21
        self.username = ""
        self.password = ""
        self.directory = ""

            
    def set_status_callback(self, callback):
        self.status_callback = callback
        
    def set_log_callback(self, callback):
        self.log_callback = callback
        
    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
            
    def update_status(self, message):
        if self.status_callback:
            self.status_callback(message)
            
    def configure(self, host, port, username, password, directory):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.directory = directory
        
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
            
        self.log(f"Server configured: {self.host}:{self.port}, Directory: {self.directory}")
        
    def start_server(self):
        if self.running:
            self.log("Server is already running")
            return False
            
        try:
            class LoggingFTPHandler(FTPHandler):
                def on_connect(handler):
                    self.log(f"Connection from: {handler.remote_ip}")
                    
                def on_disconnect(handler):
                    self.log(f"Client disconnected: {handler.remote_ip}")
                    
                def on_login(handler, username):
                    self.log(f"User logged in: {username} from {handler.remote_ip}")
                    
                def on_file_sent(handler, file):
                    self.log(f"File downloaded: {os.path.basename(file)}")
                    
                def on_file_received(handler, file):
                    self.log(f"File uploaded: {os.path.basename(file)}")
                    

            authorizer = DummyAuthorizer()
            authorizer.add_user(self.username, self.password, self.directory, perm="elradfmwMT")
            
            handler = LoggingFTPHandler
            handler.authorizer = authorizer
            handler.banner = "AES Encryption/Decryption Tool FTP Server Ready"
            
            # Check if port is available
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            
            if result == 0:
                self.log(f"Error: Port {self.port} is already in use")
                self.update_status(f"Error: Port {self.port} is already in use")
                return False
                
            # Create
            self.server = FTPServer((self.host, self.port), handler)
            
            # Set maximum connections
            self.server.max_cons = 10
            self.server.max_cons_per_ip = 5
            
            # Start server in a separate thread
            self.server_thread = threading.Thread(target=self._run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.running = True
            self.log(f"FTP Server started on {self.host}:{self.port}")
            self.update_status(f"FTP Server is running on {self.host}:{self.port}")
            return True
            
        except Exception as e:
            self.log(f"Error starting FTP server: {str(e)}")
            self.update_status(f"Error: {str(e)}")
            return False
            
    def _run_server(self):
        try:
            self.server.serve_forever()
        except Exception as e:
            self.log(f"Server thread error: {str(e)}")
            
    def stop_server(self):
        if not self.running:
            self.log("Server is not running")
            return
            
        try:
            self.server.close_all()
            self.running = False
            self.log("FTP Server stopped")
            self.update_status("FTP Server stopped")
        except Exception as e:
            self.log(f"Error stopping server: {str(e)}")
            
    def is_running(self):
        return self.running
        
    def get_connection_info(self):
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "directory": self.directory,
            "running": self.running
        }