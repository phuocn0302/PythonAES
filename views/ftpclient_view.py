import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import os
import __main__
import time

class FTPClientView:
    def __init__(self, parent, main_view):
        self.parent = parent
        self.main_view = main_view

        self.ftp_host_var = tk.StringVar(value="")
        self.ftp_port_var = tk.IntVar(value=21)
        self.ftp_username_var = tk.StringVar(value="user")
        self.ftp_password_var = tk.StringVar(value="")
        self.remote_path_var = tk.StringVar(value="/")

        main_directory = os.path.dirname(os.path.abspath(__main__.__file__))
        ftp_directory = os.path.join(main_directory, "ftp_downloads")

        self.default_directory = ftp_directory
        self.ftp_directory_var = tk.StringVar(value=ftp_directory)
        self.show_pwd_var = tk.BooleanVar()
        
        self.setup_ui()
        
    def setup_ui(self):
        self.main_container = tk.PanedWindow(self.parent, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10)
        
        self.left_panel = tk.Frame(self.main_container, padx=5)
        self.main_container.add(self.left_panel, width=500)
        
        self.right_panel = tk.Frame(self.main_container, padx=5)
        self.main_container.add(self.right_panel)
        
        self.setup_left_panel()
        self.setup_right_panel()
    
    def setup_left_panel(self):
        ttk.Label(self.left_panel, text="FTP Client Connection", font=("Arial", 14, "bold")).pack(pady=10)
        self.create_client_config(self.left_panel)
        self.create_control_buttons(self.left_panel)
        self.create_connection_info(self.left_panel)
        self.create_log_panel(self.left_panel)

    def create_log_panel(self, parent):
        self.clear_log_button = ttk.Button(parent, text="Clear Log", width=15)
        self.clear_log_button.pack(pady=5)

        log_frame = ttk.LabelFrame(parent, text="Client Log", padding=(10,10))
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.ftp_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD)
        self.ftp_log.pack(fill=tk.BOTH, expand=True)
        
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.ftp_log.insert(tk.END, f"[{current_time}] FTP Client initialized\n")
        
    def create_client_config(self, parent):
        config_frame = ttk.LabelFrame(parent, text="Connection Configuration", padding=(10,10))
        config_frame.pack(pady=5, fill=tk.X)
        
        host_frame = ttk.Frame(config_frame)
        host_frame.pack(pady=5, fill=tk.X)
        ttk.Label(host_frame, text="Host:", width=15, anchor='w').pack(side=tk.LEFT)
        ttk.Entry(host_frame, textvariable=self.ftp_host_var, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        port_frame = ttk.Frame(config_frame)
        port_frame.pack(pady=5, fill=tk.X)
        ttk.Label(port_frame, text="Port:", width=15, anchor='w').pack(side=tk.LEFT)
        ttk.Entry(port_frame, textvariable=self.ftp_port_var, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        username_frame = ttk.Frame(config_frame)
        username_frame.pack(pady=5, fill=tk.X)
        ttk.Label(username_frame, text="Username:", width=15, anchor='w').pack(side=tk.LEFT)
        ttk.Entry(username_frame, textvariable=self.ftp_username_var, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        password_frame = ttk.Frame(config_frame)
        password_frame.pack(pady=5, fill=tk.X)
        ttk.Label(password_frame, text="Password:", width=15, anchor='w').pack(side=tk.LEFT)
        self.password_entry = tk.Entry(password_frame, textvariable=self.ftp_password_var, show="*", width=30)
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Checkbutton(password_frame, text="Show", variable=self.show_pwd_var, 
                      command=self.toggle_password_visibility).pack(side=tk.RIGHT)
        
        directory_frame = ttk.Frame(config_frame)
        directory_frame.pack(pady=5, fill=tk.X)
        
        ttk.Label(directory_frame, text="Local Directory:", width=15, anchor='w').pack(side=tk.LEFT)
        ttk.Entry(directory_frame, textvariable=self.ftp_directory_var, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.browse_dir_button = ttk.Button(directory_frame, text="Browse")
        self.browse_dir_button.pack(side=tk.RIGHT)
    
    def create_control_buttons(self, parent):
        ftp_button_frame = ttk.Frame(parent)
        ftp_button_frame.pack(pady=10)
        
        self.connect_button = ttk.Button(ftp_button_frame, text="Connect", width=15, style='Accent.TButton')
        self.connect_button.pack(side=tk.LEFT, padx=5)
        
        self.disconnect_button = ttk.Button(ftp_button_frame, text="Disconnect", width=15, style='Accent.TButton')
        self.disconnect_button.pack(side=tk.LEFT, padx=5)
    
    def create_connection_info(self, parent):
        info_frame = ttk.LabelFrame(parent, text="Connection Information", padding=(10, 10))
        info_frame.pack(pady=5, fill=tk.X)
        
        self.ftp_status_label = ttk.Label(info_frame, text="Status: Disconnected", font=("Arial", 10, "bold"))
        self.ftp_status_label.pack(pady=5)
    
    def setup_right_panel(self):
        self.create_file_explorer(self.right_panel)
        self.create_transfer_controls(self.right_panel)

    def create_transfer_controls(self, parent):
        transfer_frame = ttk.Frame(parent)
        transfer_frame.pack(fill=tk.X, pady=5)
        
        self.download_button = ttk.Button(transfer_frame, text="Download", width=12)
        self.download_button.pack(side=tk.LEFT, padx=5)
        
        self.upload_button = ttk.Button(transfer_frame, text="Upload", width=12)
        self.upload_button.pack(side=tk.LEFT, padx=5)

    def create_file_explorer(self, parent):
        explorer_frame = ttk.LabelFrame(parent, text="Remote File Explorer", padding=(10, 10))
        explorer_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        explorer_container = ttk.Frame(explorer_frame)
        explorer_container.pack(fill=tk.BOTH, expand=True)
        
        nav_frame = ttk.Frame(explorer_frame)
        nav_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(nav_frame, text="Path:").pack(side=tk.LEFT, padx=5)
        path_entry = ttk.Entry(nav_frame, textvariable=self.remote_path_var, state="readonly")
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.go_up_button = ttk.Button(nav_frame, text="⬆️ Up", width=8)
        self.go_up_button.pack(side=tk.RIGHT, padx=5)
        
        # File explorer treeview
        self.file_explorer = ttk.Treeview(explorer_container, columns=("size", "modified"), show="tree headings")
        self.file_explorer.heading("#0", text="Name")
        self.file_explorer.heading("size", text="Size")
        self.file_explorer.heading("modified", text="Modified")
        self.file_explorer.column("#0", width=250, stretch=True)
        self.file_explorer.column("size", width=100, anchor="e")
        self.file_explorer.column("modified", width=150)
        self.file_explorer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add bindings for mouse events
        self.file_explorer.bind("<Double-1>", self.on_item_double_click)
        self.file_explorer.bind("<Button-3>", self.on_item_right_click)
        
        explorer_scrollbar = ttk.Scrollbar(explorer_container, orient=tk.VERTICAL, command=self.file_explorer.yview)
        explorer_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_explorer.configure(yscrollcommand=explorer_scrollbar.set)
        
        # Create context menu
        self.context_menu = tk.Menu(self.file_explorer, tearoff=0)
        self.context_menu.add_command(label="Download")
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete")
        self.context_menu.add_command(label="Rename")
        self.context_menu.add_separator()
        self.context_menu.add_command(label="New Folder")
        
        # Explorer controls
        explorer_controls = ttk.Frame(explorer_frame)
        explorer_controls.pack(fill=tk.X, pady=5)
        
        self.refresh_button = ttk.Button(explorer_controls, text="Refresh", width=10)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        self.new_folder_button = ttk.Button(explorer_controls, text="New Folder", width=10)
        self.new_folder_button.pack(side=tk.LEFT, padx=5)
        
        self.open_local_folder_button = ttk.Button(explorer_controls, text="Open Local Folder", width=15)
        self.open_local_folder_button.pack(side=tk.RIGHT, padx=5)    

    def update_file_explorer(self, file_data):
        for item in self.file_explorer.get_children():
            self.file_explorer.delete(item)
        
        # Add files and directories
        for name, is_dir, size, modified in file_data:
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            
            icon_type = "folder" if is_dir else "file"
            
            self.file_explorer.insert("", tk.END, text=' ' + name, values=(size_str, modified), 
                                    tags=(name, icon_type),
                                    image=self.get_folder_icon() if is_dir else self.get_file_icon())

    def update_remote_path(self, path):
        """Update the displayed remote path"""
        self.current_path_var.set(path)

    def set_browse_directory_command(self, command):
        self.browse_dir_button.config(command=command)
    
    def set_connect_command(self, command):
        self.connect_button.config(command=command)
    
    def set_disconnect_command(self, command):
        self.disconnect_button.config(command=command)
    
    def set_refresh_explorer_command(self, command):
        self.refresh_button.config(command=command)
    
    def set_new_folder_command(self, command):
        self.new_folder_button.config(command=command)
    
    def set_download_command(self, command):
        self.download_button.config(command=command)
    
    def set_upload_command(self, command):
        self.upload_button.config(command=command)

    def set_open_local_folder_command(self, command):
        self.open_local_folder_button.config(command=command)
    
    def set_go_up_button_command(self, command):
        self.go_up_button.config(command=command)

    def set_clear_log_command(self, command):
        self.clear_log_button.config(command=command)
    
    def toggle_password_visibility(self):
        self.password_entry.config(show='' if self.show_pwd_var.get() else '*')
    
    def update_status(self, message):
        self.ftp_status_label.config(text=message)
    
    def log_message(self, message):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.ftp_log.insert(tk.END, f"[{current_time}] {message}\n")
        self.ftp_log.see(tk.END)
    
    def clear_log(self):
        self.ftp_log.delete(1.0, tk.END)
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.ftp_log.insert(tk.END, f"[{current_time}] Log cleared\n")
    
    def on_item_double_click(self, event):
        item_id = self.file_explorer.identify_row(event.y)
        if item_id:
            if hasattr(self, 'double_click_handler'):
                self.double_click_handler(item_id)

    def on_item_right_click(self, event):
        item_id = self.file_explorer.identify_row(event.y)
        if item_id:
            self.file_explorer.selection_set(item_id)
            self.show_context_menu(event)

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def set_context_menu_commands(self, download_cmd, delete_cmd, rename_cmd, new_folder_cmd):
        self.context_menu.entryconfig("Download", command=lambda: download_cmd(self.file_explorer.selection()))
        self.context_menu.entryconfig("Delete", command=lambda: delete_cmd(self.file_explorer.selection()))
        self.context_menu.entryconfig("Rename", command=lambda: rename_cmd(self.file_explorer.selection()))
        self.context_menu.entryconfig("New Folder", command=new_folder_cmd)

    def set_double_click_handler(self, handler):
        self.double_click_handler = handler

    def update_remote_explorer(self, directory, file_data):
        for item in self.file_explorer.get_children():
            self.file_explorer.delete(item)
        
        if directory != "/":
            self.file_explorer.insert("", tk.END, text="..", values=("", ""),
                                    tags=("..", "parent-dir", "folder"),
                                    image=self.get_folder_icon())
        
        # Add files and directories
        for name, is_dir, size, modified in file_data:
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            
            icon_type = "folder" if is_dir else "file"
            
            self.file_explorer.insert("", tk.END, text=' ' + name, values=(size_str, modified), 
                                    tags=(name, icon_type),
                                    image=self.get_folder_icon() if is_dir else self.get_file_icon())

    def disable_connect_button(self):
        self.connect_button.config(state="disabled")
        
    def enable_connect_button(self):
        self.connect_button.config(state="normal")

    def get_folder_icon(self):
        """Get folder icon for treeview. Creates icon if not already cached."""
        if not hasattr(self, '_folder_icon'):
            image = Image.open('./assets/icon/folder.png')
            icon = image.resize((16,16))
            self._folder_icon = ImageTk.PhotoImage(icon)
        return self._folder_icon

    def get_file_icon(self):
        """Get file icon for treeview. Creates icon if not already cached."""
        if not hasattr(self, '_file_icon'):
            image = Image.open('./assets/icon/file.png')
            icon = image.resize((16,16))
            self._file_icon = ImageTk.PhotoImage(icon)
        return self._file_icon

    def get_host(self):
        return self.ftp_host_var.get()
    
    def get_port(self):
        return self.ftp_port_var.get()
    
    def get_username(self):
        return self.ftp_username_var.get()
    
    def get_password(self):
        return self.ftp_password_var.get()
    
    def get_directory(self):
        return self.ftp_directory_var.get()
    
    def update_remote_path(self, path):
        self.remote_path_var.set(path)