import tkinter as tk
from tkinter import ttk
from views.main_view import MainView
from controllers.encryption_controller import EncryptionController
from controllers.ftpserver_controller import FTPServerController

class MainController:
    def __init__(self, root):
        self.root = root
        self.main_view = MainView(root)
        
        self.encryption_controller = EncryptionController(self.main_view.encryption_view, self)
        
        self.ftp_controller = FTPServerController(self.main_view.ftp_server_view, self)

    def run(self):
        self.root.mainloop()