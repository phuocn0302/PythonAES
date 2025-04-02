import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import os
import __main__
import time

class FTPServerView:
    def __init__(self, parent, main_view):
        self.parent = parent
        self.main_view = main_view

        self.ftp_host_var = tk.StringVar(value="127.0.0.1")
        self.ftp_port_var = tk.IntVar(value=21)
        self.ftp_username_var = tk.StringVar(value="user")
        self.ftp_password_var = tk.StringVar(value="123")

        main_directory = os.path.dirname(os.path.abspath(__main__.__file__))
        ftp_directory = os.path.join(main_directory, "ftp_shared")

        self.default_direcory = ftp_directory
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

        ttk.Label(self.left_panel, text="FTP Server Hosting", font=("Arial", 14, "bold")).pack(pady=10)
        self.create_server_config(self.left_panel)
        self.create_control_buttons(self.left_panel)
        self.create_connection_info(self.left_panel)
        self.create_log_panel(self.left_panel)

    def create_log_panel(self, parent):
        self.clear_log_button = ttk.Button(parent, text="Clear Log", width=15)
        self.clear_log_button.pack(pady=5)

        log_frame = ttk.LabelFrame(parent, text="Server Log", padding=(10,10))
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.ftp_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD)
        self.ftp_log.pack(fill=tk.BOTH, expand=True)
        
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.ftp_log.insert(tk.END, f"[{current_time}] FTP Server initialized\n")
        
    def create_server_config(self, parent):
        config_frame = ttk.LabelFrame(parent, text="Server Configuration", padding=(10,10))
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
        
        ttk.Label(directory_frame, text="Directory:", width=15, anchor='w').pack(side=tk.LEFT)
        ttk.Entry(directory_frame, textvariable=self.ftp_directory_var, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.browse_dir_button = ttk.Button(directory_frame, text="Browse")
        self.browse_dir_button.pack(side=tk.RIGHT)
    
    def create_control_buttons(self, parent):
        ftp_button_frame = ttk.Frame(parent)
        ftp_button_frame.pack(pady=10)
        
        self.start_button = ttk.Button(ftp_button_frame, text="Start Server", width=15, style='Accent.TButton')
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(ftp_button_frame, text="Stop Server", width=15, style='Accent.TButton')
        self.stop_button.pack(side=tk.LEFT, padx=5)
    
    def create_connection_info(self, parent):
        info_frame = ttk.LabelFrame(parent, text="Connection Information", padding=(10, 10))
        info_frame.pack(pady=5, fill=tk.X)
        
        self.ftp_status_label = ttk.Label(info_frame, text="Server Status: Stopped", font=("Arial", 10, "bold"))
        self.ftp_status_label.pack(pady=5)
    
    def setup_right_panel(self):
        self.create_file_explorer(self.right_panel)

    def create_file_explorer(self, parent):
        explorer_frame = ttk.LabelFrame(parent, text="File Explorer", padding=(10, 10))
        explorer_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        explorer_container = ttk.Frame(explorer_frame)
        explorer_container.pack(fill=tk.BOTH, expand=True)
        
        nav_frame = ttk.Frame(explorer_frame)
        nav_frame.pack(fill=tk.X, pady=5)
        
        self.current_path_var = tk.StringVar(value="")
        ttk.Label(nav_frame, text="Path:").pack(side=tk.LEFT, padx=5)
        path_entry = ttk.Entry(nav_frame, textvariable=self.current_path_var, state="readonly")
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
        self.context_menu.add_command(label="Open")
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete")
        self.context_menu.add_command(label="Rename")
        
        # Explorer controls
        explorer_controls = ttk.Frame(explorer_frame)
        explorer_controls.pack(fill=tk.X, pady=5)
        
        self.refresh_button = ttk.Button(explorer_controls, text="Refresh", width=10)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        self.new_folder_button = ttk.Button(explorer_controls, text="New Folder", width=10)
        self.new_folder_button.pack(side=tk.LEFT, padx=5)

        self.new_file_button = ttk.Button(explorer_controls, text="New File", width=10)
        self.new_file_button.pack(side=tk.LEFT, padx=5)

        self.choose_file_button = ttk.Button(explorer_controls, text="Choose File", width=10)
        self.choose_file_button.pack(side=tk.LEFT, padx=5)

        self.open_folder_button = ttk.Button(explorer_controls, text="Open in Explorer", width=15)
        self.open_folder_button.pack(side=tk.RIGHT, padx=5)    

    def set_browse_directory_command(self, command):
        self.browse_dir_button.config(command=command)
    
    def set_start_server_command(self, command):
        self.start_button.config(command=command)
    
    def set_stop_server_command(self, command):
        self.stop_button.config(command=command)
    
    def set_refresh_explorer_command(self, command):
        self.refresh_button.config(command=command)
    
    def set_new_folder_command(self, command):
        self.new_folder_button.config(command=command)

    def set_new_file_command(self, command):
        self.new_file_button.config(command=command)

    def set_choose_file_command(self, command):
        self.choose_file_button.config(command=command)

    def set_open_folder_command(self, command):
        self.open_folder_button.config(command=command)
    
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

    def set_context_menu_commands(self, open_cmd, delete_cmd, rename_cmd):
        self.context_menu.entryconfig("Open", command=lambda: open_cmd(self.file_explorer.selection()))
        self.context_menu.entryconfig("Delete", command=lambda: delete_cmd(self.file_explorer.selection()))
        self.context_menu.entryconfig("Rename", command=lambda: rename_cmd(self.file_explorer.selection()))

    def set_double_click_handler(self, handler):
        self.double_click_handler = handler

    def update_file_explorer(self, directory, file_data):
        for item in self.file_explorer.get_children():
            self.file_explorer.delete(item)
        
        parent_dir = os.path.dirname(directory)
        if parent_dir != directory:
            self.file_explorer.insert("", tk.END, text="  ..", values=("", ""),
                                    tags=(parent_dir, "folder"),
                                    image=self.get_folder_icon())
        
        # Add files and directories
        for name, is_dir, size, modified in file_data:
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            
            # Store full file path and is_dir info as tags for later use
            item_path = os.path.join(directory, name)
            icon_type = "folder" if is_dir else "file"
            
            self.file_explorer.insert("", tk.END, text='  ' + name, values=(size_str, modified), 
                                    tags=(item_path, icon_type),
                                    image=self.get_folder_icon() if is_dir else self.get_file_icon())

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