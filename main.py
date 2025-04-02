import tkinter as tk
import sv_ttk

from controllers.main_controller import MainController

if __name__ == "__main__":
    root = tk.Tk()
    app = MainController(root)
    # sv_ttk.use_light_theme()
    app.run()