import tkinter as tk
from tkinter import ttk, messagebox
from views.encryption_view import EncryptionView
from views.ftpserver_view import FTPServerView
from views.ftpclient_view import FTPClientView


class MainView:
    def __init__(self, root):
        self.root = root
        self.root.title("AES Tool")
        self.root.geometry("1280x800")
        self.root.resizable(True, True)
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.encryption_tab = ttk.Frame(self.notebook)
        self.ftp_server_tab = ttk.Frame(self.notebook)
        self.ftp_client_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.encryption_tab, text="Encryption/Decryption")
        self.notebook.add(self.ftp_server_tab, text="FTP Server")
        self.notebook.add(self.ftp_client_tab, text="FTP Client")
        
        self.encryption_view = EncryptionView(self.encryption_tab, self)
        self.ftp_server_view = FTPServerView(self.ftp_server_tab, self)
        self.ftp_client_view = FTPClientView(self.ftp_client_tab, self)
    

    
    def show_error(self, title, message):
        messagebox.showerror(title, message)
    
    def show_info(self, title, message):
        messagebox.showinfo(title, message)
    
    def get_encryption_tab(self):
        return self.encryption_tab
    
    def get_ftp_tab(self):
        return self.ftp_server_tab