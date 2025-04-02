import os
import time
import sys
import subprocess
from tkinter import filedialog, messagebox
from tkinter.simpledialog import askstring
from models.ftp_model import FTPServerManager
from views.ftpserver_view import FTPServerView

class FTPServerController:
    def __init__(self, view: FTPServerView, main_controller):
        self.view = view
        self.main_controller = main_controller

        self.manager = FTPServerManager()
        self.manager.set_status_callback(self.update_status)
        self.manager.set_log_callback(self.log_message)

        self.view.set_browse_directory_command(self.browse_directory)
        self.view.set_start_server_command(self.start_server)
        self.view.set_stop_server_command(self.stop_server)
        self.view.set_clear_log_command(self.clear_log)
        
        self.view.set_refresh_explorer_command(self.refresh_explorer)
        self.view.set_open_folder_command(self.open_folder)
        self.view.set_go_up_button_command(self.navigate_up)
        self.view.set_new_folder_command(self.create_new_folder)
        self.view.set_new_file_command(self.create_new_file)
        self.view.set_choose_file_command(self.choose_file)

        self.view.set_context_menu_commands(
            self.open_file,
            self.delete_file,
            self.rename_file
        )
        
        self.view.set_double_click_handler(self.handle_item_double_click)
        
        self.refresh_explorer()

    def apply_settings(self):
        try:
            self.manager.configure(
                self.view.get_host(),
                self.view.get_port(),
                self.view.get_username(),
                self.view.get_password(),
                self.view.get_directory()
            )
            self.log_message("Settings applied successfully")
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))

    def start_server(self):
        if self.manager.is_running():
            messagebox.showinfo("Info", "Server is already running")
            return

        try:
            self.apply_settings()
            if self.manager.start_server():
                self.update_status("Server Status: Running")
                messagebox.showinfo("Success", "FTP Server started successfully")
            else:
                messagebox.showerror("Error", "Failed to start FTP Server")
        except Exception as e:
            self.log_message(f"Error starting server: {str(e)}")
            messagebox.showerror("Error", str(e))

    def stop_server(self):
        if not self.manager.is_running():
            messagebox.showinfo("Info", "Server is not running")
            return

        self.manager.stop_server()
        self.update_status("Server Status: Stopped")

    def get_directory(self):
        dir = self.view.get_directory()
        os.makedirs(dir, exist_ok=True)
        
        return dir

    def navigate_up(self):
        current_dir = self.view.get_directory()
        if current_dir == self.view.default_direcory:
            return

        parent_dir = os.path.dirname(current_dir)
        
        if os.path.exists(parent_dir) and parent_dir != current_dir:
            self.view.ftp_directory_var.set(parent_dir)
            self.refresh_explorer()

    def create_new_folder(self):
        current_dir = self.view.get_directory()
        
        folder_name = askstring("New Folder", "Enter folder name:")
        
        if folder_name:
            try:
                new_folder_path = os.path.join(current_dir, folder_name)
                os.makedirs(new_folder_path, exist_ok=False)
                self.log_message(f"Created new folder: {new_folder_path}")
                self.refresh_explorer()
            except FileExistsError:
                messagebox.showerror("Error", f"Folder '{folder_name}' already exists")
            except Exception as e:
                self.log_message(f"Error creating folder: {str(e)}")
                messagebox.showerror("Error", f"Could not create folder: {str(e)}")

    def create_new_file(self):
        current_dir = self.view.get_directory()
        
        file_name = askstring("New File", "Enter file name:")
        
        if file_name:
            try:
                new_file_path = os.path.join(current_dir, file_name)
                
                if os.path.exists(new_file_path):
                    messagebox.showerror("Error", f"File '{file_name}' already exists")
                    return
                
                with open(new_file_path, 'w') as file:
                    pass 
                
                self.log_message(f"Created new file: {new_file_path}")
                self.refresh_explorer()
            except Exception as e:
                self.log_message(f"Error creating file: {str(e)}")
                messagebox.showerror("Error", f"Could not create file: {str(e)}")

    def open_folder(self):
        directory = self.get_directory();
        try:
            os.startfile(directory)
            self.log_message(f"Opened directory: {directory}")
        except Exception as e:
            self.log_message(f"Error opening directory: {str(e)}")

    def browse_directory(self):
        directory = filedialog.askdirectory(
            title="Select FTP Shared Directory",
            initialdir=self.view.get_directory()
        )
        if directory:
            self.view.ftp_directory_var.set(directory)
            self.refresh_explorer()

    def handle_item_double_click(self, item_id):
        item_data = self.view.file_explorer.item(item_id)
        if not item_id or not item_data:
            return
        
        tags = self.view.file_explorer.item(item_id, "tags")
        if not tags:
            return
        
        file_path = tags[0]
        is_dir = "folder" in tags
        
        if is_dir:
            self.view.ftp_directory_var.set(file_path)
            self.refresh_explorer()
            # self.view.ftp_directory_var.set(view.default_direcory)
        else:
            self.open_file_by_path(file_path)

    def choose_file(self):
        item_id = self.view.file_explorer.selection()
        tags = self.view.file_explorer.item(item_id, "tags")
        
        if tags and not "folder" in tags:
            self.view.main_view.notebook.select(self.view.main_view.encryption_tab)
            file_path = str(tags[0]).replace("\\", "/")
            self.main_controller.encryption_controller.browse_file(file_path)
        else:
            messagebox.showerror("Error", f"Not a file")
            return

        

    def open_file(self, selection):
        if not selection:
            return
        
        item_id = selection[0]
        tags = self.view.file_explorer.item(item_id, "tags")
        if tags:
            file_path = tags[0]
            self.open_file_by_path(file_path)

    def open_file_by_path(self, file_path):
        try:
            if sys.platform.startswith("win"):
                subprocess.run(["notepad", file_path], check=True)
            else:
                subprocess.run(["xdg-open", file_path], check=True)
            self.log_message(f"Opened file: {file_path}")
        except Exception as e:
            self.log_message(f"Error opening file: {str(e)}")
            messagebox.showerror("Error", f"Could not open file: {str(e)}")


    def delete_file(self, selection):
        if not selection:
            return
        
        item_id = selection[0]
        item_name = self.view.file_explorer.item(item_id, "text")
        tags = self.view.file_explorer.item(item_id, "tags")
        
        if not tags:
            return
        
        file_path = tags[0]
        is_dir = "folder" in tags
        
        # Confirm deletion
        if is_dir:
            confirm = messagebox.askyesno("Confirm Delete", 
                                        f"Are you sure you want to delete the folder '{item_name}' and all its contents?")
        else:
            confirm = messagebox.askyesno("Confirm Delete", 
                                        f"Are you sure you want to delete the file '{item_name}'?")
        
        if confirm:
            try:
                import shutil
                if is_dir:
                    shutil.rmtree(file_path)
                    self.log_message(f"Deleted folder: {file_path}")
                else:
                    os.remove(file_path)
                    self.log_message(f"Deleted file: {file_path}")
                
                # Refresh the explorer to show changes
                self.refresh_explorer()
            except Exception as e:
                self.log_message(f"Error deleting: {str(e)}")
                messagebox.showerror("Error", f"Could not delete: {str(e)}")

    def rename_file(self, selection):
        if not selection:
            return
        
        item_id = selection[0]
        old_name = self.view.file_explorer.item(item_id, "text")
        tags = self.view.file_explorer.item(item_id, "tags")
        
        if not tags:
            return
        
        file_path = tags[0]
        
        
        new_name = askstring("Rename", "Enter new name:", initialvalue=old_name)
        
        if new_name and new_name != old_name:
            try:
                new_path = os.path.join(os.path.dirname(file_path), new_name)
                os.rename(file_path, new_path)
                self.log_message(f"Renamed: {old_name} to {new_name}")
                
                # Refresh the explorer to show changes
                self.refresh_explorer()
            except Exception as e:
                self.log_message(f"Error renaming: {str(e)}")
                messagebox.showerror("Error", f"Could not rename: {str(e)}")

    def refresh_explorer(self):
        directory = self.view.get_directory()
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                self.log_message(f"Created directory: {directory}")
            except Exception as e:
                self.log_message(f"Error creating directory: {str(e)}")
                return
        
        self.view.current_path_var.set(directory)
        
        try:
            file_data = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                try:
                    size = os.path.getsize(item_path)
                    modified = time.strftime("%Y-%m-%d %H:%M:%S", 
                        time.localtime(os.path.getmtime(item_path)))
                    is_dir = os.path.isdir(item_path)
                    file_data.append((item, is_dir, size, modified))
                except Exception as e:
                    self.log_message(f"Error accessing {item}: {str(e)}")
            
            # Sort directories first, then files
            file_data.sort(key=lambda x: (not x[1], x[0].lower()))
            
            self.view.update_file_explorer(directory, file_data)
        except Exception as e:
            self.log_message(f"Error refreshing explorer: {str(e)}")

    def update_status(self, message):
        self.view.update_status(message)

    def log_message(self, message):
        self.view.log_message(message)

    def clear_log(self):
        self.view.clear_log()