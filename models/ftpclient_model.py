import os
import ftplib

class FTPClientManager:
    def __init__(self):
        self.client = None
        self.connected = False
        self.status_callback = None
        self.log_callback = None
        
        self.host = ""
        self.port = 21
        self.username = ""
        self.password = ""
        self.local_directory = ""
        self.remote_directory = "/"
        
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
            
    def configure(self, host, port, username, password, local_directory):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.local_directory = local_directory
        
        if not os.path.exists(self.local_directory):
            os.makedirs(self.local_directory)
            
        self.log(f"Client configured: {self.host}:{self.port}, Local Directory: {self.local_directory}")
        
    def connect(self):
        if self.connected:
            self.log("Already connected to server")
            return False
            
        try:
            self.client = ftplib.FTP()
            self.client.connect(self.host, self.port, timeout=10)
            self.client.login(self.username, self.password)
            
            self.connected = True
            self.log(f"Connected to FTP server at {self.host}:{self.port}")
            self.update_status(f"Connected to {self.host}:{self.port}")
            
            # Get initial directory
            self.remote_directory = self.client.pwd()
            
            return True
        except Exception as e:
            self.log(f"Error connecting to FTP server: {str(e)}")
            self.update_status(f"Connection error: {str(e)}")
            return False
            
    def disconnect(self):
        if not self.connected:
            self.log("Not connected to a server")
            return
            
        try:
            self.client.quit()
            self.connected = False
            self.log("Disconnected from FTP server")
            self.update_status("Disconnected from server")
        except Exception as e:
            self.log(f"Error disconnecting: {str(e)}")
            
    def is_connected(self):
        return self.connected
    
    def get_remote_directory(self):
        if not self.connected:
            return "/"
        try:
            self.remote_directory = self.client.pwd()
            return self.remote_directory
        except Exception as e:
            self.log(f"Error getting remote directory: {str(e)}")
            return "/"
    
    def change_remote_directory(self, path):
        if not self.connected:
            self.log("Not connected to server")
            return False
        
        try:
            self.client.cwd(path)
            self.remote_directory = self.client.pwd()
            self.log(f"Changed to directory: {self.remote_directory}")
            return True
        except Exception as e:
            self.log(f"Error changing directory: {str(e)}")
            return False
    
    def list_remote_files(self):
        if not self.connected:
            self.log("Not connected to server")
            return []
        
        try:
            # Get file listing with details
            file_data = []
            
            def process_line(line):
                parts = line.split()
                if len(parts) < 9:
                    return
                
                # Parse a typical FTP LIST output
                permissions = parts[0]
                is_dir = permissions.startswith('d')
                size = int(parts[4])
                
                # Month, day and either year or time
                date_parts = parts[5:8]
                modified = " ".join(date_parts)
                
                # Get filename (could contain spaces)
                filename = " ".join(parts[8:])
                
                file_data.append((filename, is_dir, size, modified))
            
            self.client.retrlines('LIST', process_line)
            return file_data
            
        except Exception as e:
            self.log(f"Error listing remote files: {str(e)}")
            return []
    
    def download_file(self, remote_filename, local_filename=None):
        if not self.connected:
            self.log("Not connected to server")
            return False
        
        if local_filename is None:
            local_filename = os.path.join(self.local_directory, remote_filename)
        
        try:
            with open(local_filename, 'wb') as local_file:
                self.log(f"Downloading {remote_filename}...")
                self.client.retrbinary(f'RETR {remote_filename}', local_file.write)
            
            self.log(f"Downloaded {remote_filename} to {local_filename}")
            return True
        except Exception as e:
            self.log(f"Error downloading file: {str(e)}")
            # Remove partial file if download failed
            if os.path.exists(local_filename):
                try:
                    os.remove(local_filename)
                except:
                    pass
            return False
    
    def upload_file(self, local_filename, remote_filename=None):
        if not self.connected:
            self.log("Not connected to server")
            return False
        
        if not os.path.exists(local_filename):
            self.log(f"Local file not found: {local_filename}")
            return False
        
        if remote_filename is None:
            remote_filename = os.path.basename(local_filename)
        
        try:
            with open(local_filename, 'rb') as local_file:
                self.log(f"Uploading {local_filename}...")
                self.client.storbinary(f'STOR {remote_filename}', local_file)
            
            self.log(f"Uploaded {local_filename} to {remote_filename}")
            return True
        except Exception as e:
            self.log(f"Error uploading file: {str(e)}")
            return False
    
    def create_remote_directory(self, dirname):
        if not self.connected:
            self.log("Not connected to server")
            return False
        
        try:
            self.client.mkd(dirname)
            self.log(f"Created remote directory: {dirname}")
            return True
        except Exception as e:
            self.log(f"Error creating remote directory: {str(e)}")
            return False
    
    def delete_remote_file(self, filename):
        if not self.connected:
            self.log("Not connected to server")
            return False
        
        try:
            self.client.delete(filename)
            self.log(f"Deleted remote file: {filename}")
            return True
        except Exception as e:
            self.log(f"Error deleting remote file: {str(e)}")
            return False
    
    def delete_remote_directory(self, dirname):
        if not self.connected:
            self.log("Not connected to server")
            return False
        
        try:
            self.client.rmd(dirname)
            self.log(f"Deleted remote directory: {dirname}")
            return True
        except Exception as e:
            self.log(f"Error deleting remote directory: {str(e)}")
            return False
    
    def rename_remote_file(self, old_name, new_name):
        if not self.connected:
            self.log("Not connected to server")
            return False
        
        try:
            self.client.rename(old_name, new_name)
            self.log(f"Renamed remote file: {old_name} to {new_name}")
            return True
        except Exception as e:
            self.log(f"Error renaming remote file: {str(e)}")
            return False
            
    def get_connection_info(self):
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "local_directory": self.local_directory,
            "remote_directory": self.remote_directory,
            "connected": self.connected
        }