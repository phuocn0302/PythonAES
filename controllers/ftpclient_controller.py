import os
import threading
import time
import sys
import subprocess
from tkinter import filedialog, messagebox
from tkinter.simpledialog import askstring
from models.ftpclient_model import FTPClientManager
from views.ftpclient_view import FTPClientView

class FTPClientController:
    def __init__(self, view: FTPClientView, main_controller):
        self.view = view
        self.main_controller = main_controller

        self.manager = FTPClientManager()
        self.manager.set_status_callback(self.update_status)
        self.manager.set_log_callback(self.log_message)

        self.view.set_browse_directory_command(self.browse_directory)
        self.view.set_connect_command(self.connect_to_server)
        self.view.set_disconnect_command(self.disconnect_from_server)
        self.view.set_clear_log_command(self.clear_log)
        
        self.view.set_refresh_explorer_command(self.refresh_explorer)
        self.view.set_open_local_folder_command(self.open_local_folder)
        self.view.set_go_up_button_command(self.navigate_up)
        self.view.set_new_folder_command(self.create_new_folder)
        self.view.set_download_command(self.download_selected)
        self.view.set_upload_command(self.upload_file)
        self.view.set_choose_file_command(self.choose_file)

        self.view.set_context_menu_commands(
            self.download_file,
            self.delete_remote_file,
            self.rename_remote_file,
            self.create_new_folder
        )
        
        self.view.set_double_click_handler(self.handle_item_double_click)

    def apply_settings(self):
        try:
            self.manager.configure(
                self.view.get_host(),
                self.view.get_port(),
                self.view.get_username(),
                self.view.get_password(),
                self.view.get_directory()
            )
            self.log_message("Connection settings applied")
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))

    def connect_to_server(self):
        if self.manager.is_connected():
            messagebox.showinfo("Info", "Already connected to server")
            return


        try:
            self.apply_settings()
            self.update_status("Status: Connecting to server...")
            self.log_message(f"Connecting to {self.view.get_host()}:{self.view.get_port()}...")
            
            self.view.disable_connect_button()
            

            def connection_thread():
                try:
                    connection_success = self.manager.connect()
                    
                    self.view.parent.after(0, lambda: self._handle_connection_result(connection_success))
                except Exception as e:
                    error_msg = str(e)
                    self.view.parent.after(0, lambda: self._handle_connection_error(error_msg))
            
            
            thread = threading.Thread(target=connection_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.log_message(f"Error preparing connection: {str(e)}")
            messagebox.showerror("Error", str(e))
            self.view.enable_connect_button()

    def _handle_connection_result(self, success):
        if success:
            self.update_status(f"Status: Connected to {self.view.get_host()}")
            messagebox.showinfo("Success", "Connected to FTP Server")
            self.refresh_explorer()
        else:
            messagebox.showerror("Error", "Failed to connect to FTP Server")
        
        self.view.enable_connect_button()

    def _handle_connection_error(self, error_msg):
        self.log_message(f"Error connecting to server: {error_msg}")
        messagebox.showerror("Error", error_msg)
        self.update_status("Status: Connection failed")
        self.view.enable_connect_button()

    def check_server_connection(self):
        if not self.manager.is_connected():
            return False

        try:
            # Try to execute a simple command to test if the server is still responsive
            self.manager.client.voidcmd("NOOP")
            return True
        except Exception:
            # If the command fails, the server is likely disconnected
            self.handle_server_disconnection()
            return False

    def handle_server_disconnection(self):
        if self.manager.connected:
            self.log_message("Server connection lost. The server may have been shut down.")
            self.update_status("Status: Disconnected (Server shutdown)")
            

            self.manager.connected = False
            self.manager.client = None
            
            for item in self.view.file_explorer.get_children():
                self.view.file_explorer.delete(item)
                
            messagebox.showwarning("Connection Lost", 
                                "Connection to the FTP server was lost. The server may have been shut down.")

    def disconnect_from_server(self):
        if not self.manager.is_connected():
            messagebox.showinfo("Info", "Not connected to a server")
            return

        self.manager.disconnect()
        self.update_status("Status: Disconnected")
        
        for item in self.view.file_explorer.get_children():
            self.view.file_explorer.delete(item)

    def get_local_directory(self):
        dir = self.view.get_directory()
        os.makedirs(dir, exist_ok=True)
        
        return dir

    def navigate_up(self):
        if not self.check_server_connection():
            messagebox.showinfo("Info", "Not connected to a server")
            return

        try:
            current_dir = self.manager.get_remote_directory()
            if current_dir == "/" or current_dir == "":
                return
            
            # Go up one directory
            self.manager.change_remote_directory("..")
            self.view.update_remote_path(self.manager.get_remote_directory())
            self.refresh_explorer()
        except Exception as e:
            self.log_message(f"Error navigating up: {str(e)}")

    def create_new_folder(self):
        if not self.check_server_connection():
            messagebox.showinfo("Info", "Not connected to a server")
            return

        folder_name = askstring("New Remote Folder", "Enter folder name:")
        
        if folder_name:
            try:
                if self.manager.create_remote_directory(folder_name):
                    self.refresh_explorer()
            except Exception as e:
                self.log_message(f"Error creating folder: {str(e)}")
                messagebox.showerror("Error", f"Could not create folder: {str(e)}")

    def open_local_folder(self):
        directory = self.get_local_directory()
        try:
            if sys.platform.startswith("win"):
                os.startfile(directory)
            else:
                subprocess.run(["xdg-open", directory], check=True)
            self.log_message(f"Opened local directory: {directory}")
        except Exception as e:
            self.log_message(f"Error opening directory: {str(e)}")

    def browse_directory(self):
        directory = filedialog.askdirectory(
            title="Select Local Download Directory",
            initialdir=self.view.get_directory()
            )
        if directory and directory != self.view.get_directory():
            self.view.directory_var.set(directory)
            self.log_message(f"Local directory changed to: {directory}")

    def refresh_explorer(self):
        if not self.check_server_connection():
            messagebox.showinfo("Info", "Not connected to a server")
            return
        
        try:
            files_data = self.manager.list_remote_files()
            current_dir = self.manager.get_remote_directory()
            self.view.update_remote_path(current_dir)
            self.view.update_file_explorer(files_data)
            self.log_message(f"Refreshed file explorer for {current_dir}")
        except Exception as e:
            self.log_message(f"Error refreshing explorer: {str(e)}")
    
    def handle_item_double_click(self, item_id):
        if not self.check_server_connection():
            return

        try:
            item = self.view.file_explorer.item(item_id)
            name = item['text'].strip()
            tags = self.view.file_explorer.item(item_id, 'tags')
            
            if not tags:
                return
                
            is_dir = 'folder' in tags
            
            if name == "..":  # Parent directory
                self.navigate_up()
                return
                
            if is_dir:
                if self.manager.change_remote_directory(name):
                    self.refresh_explorer()
            else:
                # Download the file
                self.download_file(item_id)
        except Exception as e:
            self.log_message(f"Error handling double click: {str(e)}")
    
    def download_file(self, item_id):
        if not self.check_server_connection():
            messagebox.showinfo("Info", "Not connected to a server")
            return
        
        try:
            item = self.view.file_explorer.item(item_id)
            name = item['text'].strip()
            tags = self.view.file_explorer.item(item_id, 'tags')
            
            if not tags or 'folder' in tags:
                return  # Ignore folders
                
            local_directory = self.get_local_directory()
            local_path = os.path.join(local_directory, name)
            
            if self.manager.download_file(name, local_path):
                messagebox.showinfo("Success", f"File downloaded to {local_path}")
        except Exception as e:
            self.log_message(f"Error downloading file: {str(e)}")
            messagebox.showerror("Error", str(e))
    
    def download_selected(self):
        if not self.check_server_connection():
            messagebox.showinfo("Info", "Not connected to a server")
            return
            
        selected_items = self.view.file_explorer.selection()
        if not selected_items:
            messagebox.showinfo("Info", "No files selected")
            return
            
        success_count = 0
        for item_id in selected_items:
            item = self.view.file_explorer.item(item_id)
            name = item['text'].strip()
            tags = self.view.file_explorer.item(item_id, 'tags')
            
            if not tags or 'folder' in tags:
                continue  # Skip folders
                
            local_directory = self.get_local_directory()
            local_path = os.path.join(local_directory, name)
            
            if self.manager.download_file(name, local_path):
                success_count += 1
                
        if success_count > 0:
            messagebox.showinfo("Success", f"Downloaded {success_count} file(s)")
        else:
            messagebox.showinfo("Info", "No files were downloaded")
    
    def upload_file(self):
        if not self.check_server_connection():
            messagebox.showinfo("Info", "Not connected to a server")
            return
            
        local_directory = self.get_local_directory()
        file_path = filedialog.askopenfilename(
            title="Select File to Upload",
            initialdir=local_directory
        )
        
        if not file_path:
            return
            
        try:
            filename = os.path.basename(file_path)
            if self.manager.upload_file(file_path, filename):
                self.refresh_explorer()
                messagebox.showinfo("Success", f"Uploaded {filename}")
            else:
                messagebox.showerror("Error", "Failed to upload file")
        except Exception as e:
            self.log_message(f"Error uploading file: {str(e)}")
            messagebox.showerror("Error", str(e))
    
    def delete_remote_file(self, items):
        if not self.check_server_connection() or not items:
            return
            
        try:
            for item_id in items:
                item = self.view.file_explorer.item(item_id)
                name = item['text'].strip()
                tags = self.view.file_explorer.item(item_id, 'tags')
                
                if not tags:
                    continue
                    
                is_dir = 'folder' in tags
                
                if name == "..":  # Ignore parent directory entry
                    continue
                
                confirm = messagebox.askyesno(
                    "Confirm Delete", 
                    f"Are you sure you want to delete {name}?"
                )
                
                if not confirm:
                    continue
                    
                if is_dir:
                    success = self.manager.delete_remote_directory(name)
                else:
                    success = self.manager.delete_remote_file(name)
                    
                if success:
                    self.refresh_explorer()
        except Exception as e:
            self.log_message(f"Error deleting remote item: {str(e)}")
            messagebox.showerror("Error", str(e))
    
    def rename_remote_file(self, items):
        if not self.check_server_connection() or not items:
            return
            
        try:
            item_id = items[0]  # Only handle the first selected item
            item = self.view.file_explorer.item(item_id)
            old_name = item['text'].strip()
            
            if old_name == "..":  # Ignore parent directory entry
                return
                
            new_name = askstring("Rename", "Enter new name:", initialvalue=old_name)
            
            if new_name and new_name != old_name:
                if self.manager.rename_remote_file(old_name, new_name):
                    self.refresh_explorer()
        except Exception as e:
            self.log_message(f"Error renaming remote item: {str(e)}")
            messagebox.showerror("Error", str(e))
    
    def choose_file(self):
        if not self.check_server_connection():
            messagebox.showinfo("Info", "Not connected to a server")
            return
        
        try:
            item_id = self.view.file_explorer.selection()
            item = self.view.file_explorer.item(item_id)
            name = item['text'].strip()
            tags = self.view.file_explorer.item(item_id, 'tags')
            
            if not tags or 'folder' in tags:
                return 
                
            local_directory = self.get_local_directory()
            local_path = os.path.join(local_directory, name)
            
            if self.manager.download_file(name, local_path):
                messagebox.showinfo("Success", f"File downloaded to {local_path}, now switching to encryption tab")
                self.view.main_view.notebook.select(self.view.main_view.encryption_tab)
                self.main_controller.encryption_controller.browse_file(local_path)
                
        except Exception as e:
            self.log_message(f"Error downloading file: {str(e)}")
            messagebox.showerror("Error", str(e))

    def clear_log(self):
        self.view.clear_log()
    
    def update_status(self, message):
        self.view.update_status(message)
    
    def log_message(self, message):
        self.view.log_message(message)