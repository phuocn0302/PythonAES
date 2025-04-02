import tkinter as tk
from tkinter import ttk, scrolledtext
import os

class EncryptionView:
    def __init__(self, parent, main_view):
        self.parent = parent
        self.main_view = main_view

        self.key_var = tk.StringVar()
        self.file_display_var = tk.StringVar(value="No file selected")
        self.show_key_var = tk.BooleanVar()

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
        ttk.Label(self.left_panel, text="AES Cipher", font=("Arial", 14, "bold")).pack(pady=10)
        self.create_input_settings_frame(self.left_panel)
        self.create_operation_buttons(self.left_panel)
        self.create_benchmark_frame(self.left_panel)
    
    def create_input_settings_frame(self, parent):
        input_frame = ttk.LabelFrame(parent, text="Input Settings", padding=(10,5))
        input_frame.pack(pady=5, fill=tk.X)

        key_frame = ttk.Frame(input_frame)
        key_frame.pack(pady=5, fill=tk.X)
        ttk.Label(key_frame, text="Encryption Key:", width=15, anchor='w').pack(side=tk.LEFT)

        self.key_entry = ttk.Entry(key_frame, textvariable=self.key_var, show="*", width=20)
        self.key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Checkbutton(key_frame, text="Show", variable=self.show_key_var, command=self.toggle_key_visibility).pack(side=tk.RIGHT)
        
        file_frame = ttk.Frame(input_frame)
        file_frame.pack(pady=5, fill=tk.X)
        ttk.Label(file_frame, text="Selected File:", width=15, anchor='w').pack(side=tk.LEFT)
        
        self.file_display = ttk.Label(file_frame, textvariable=self.file_display_var, width=30, anchor='w')
        self.file_display.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.browse_button = ttk.Button(input_frame, text="Browse File", width=20)
        self.browse_button.pack(pady=5)
    
    def create_operation_buttons(self, parent):
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=10)

        self.encrypt_button = ttk.Button(button_frame, text="Encrypt File", width=15, style='Accent.TButton')
        self.encrypt_button.pack(side=tk.LEFT, padx=5)

        self.decrypt_button = ttk.Button(button_frame, text="Decrypt File", width=15, style='Accent.TButton')
        self.decrypt_button.pack(side=tk.LEFT, padx=5)
    
    def create_benchmark_frame(self, parent):
        benchmark_frame = ttk.LabelFrame(parent, text="Benchmarking Results", padding=(10,10))
        benchmark_frame.pack(pady=5, fill=tk.BOTH, expand=True)
        ttk.Label(benchmark_frame, text="Round Timings:", anchor='w').pack(fill=tk.X, pady=(5, 0))

        rounds_frame = ttk.Frame(benchmark_frame)
        rounds_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.rounds_tree = ttk.Treeview(rounds_frame, columns=("round", "time"), show="headings", height=6)
        self.rounds_tree.heading("round", text="Round")
        self.rounds_tree.heading("time", text="Time (ms)")
        self.rounds_tree.column("round")
        self.rounds_tree.column("time")
        self.rounds_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        rounds_scrollbar = ttk.Scrollbar(rounds_frame, orient=tk.VERTICAL, command=self.rounds_tree.yview)
        rounds_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.rounds_tree.configure(yscrollcommand=rounds_scrollbar.set)

        ttk.Label(benchmark_frame, text="Summary Statistics:", anchor='w').pack(fill=tk.X, pady=(10, 0))

        self.stats_text = scrolledtext.ScrolledText(benchmark_frame, wrap=tk.WORD, height=6)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        self.stats_text.configure(state="disabled")
    
    def setup_right_panel(self):
        container = ttk.Frame(self.right_panel)
        container.pack(fill=tk.BOTH, expand=True)

        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)

        input_frame = ttk.LabelFrame(container, text="Input File Content", padding=(5,5))
        input_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, expand=True)
        self.input_text.configure(state="disabled")

        output_frame = ttk.LabelFrame(container, text="Output File Content", padding=(5,5))
        output_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.configure(state="disabled")

    def toggle_key_visibility(self):
        self.key_entry.config(show='' if self.show_key_var.get() else '*')
    
    def set_browse_command(self, command):
        self.browse_button.config(command=command)
    
    def set_encrypt_command(self, command):
        self.encrypt_button.config(command=command)
    
    def set_decrypt_command(self, command):
        self.decrypt_button.config(command=command)
    
    def update_file_display(self, filename):
        self.file_display_var.set(os.path.basename(filename) if filename else "No file selected")
    
    def set_input_text(self, content):
        self.input_text.configure(state="normal")
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(tk.END, content)
        self.input_text.configure(state="disabled")
    
    def set_output_text(self, content):
        self.output_text.configure(state="normal")
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, content)
        self.output_text.configure(state="disabled")
    
    def get_encryption_key(self):
        return self.key_var.get()
    
    def update_round_timings(self, round_timings):
        for item in self.rounds_tree.get_children():
            self.rounds_tree.delete(item)
        for i, timing in enumerate(round_timings):
            if i == 0:
                self.rounds_tree.insert("", tk.END, values=(f"Initial AddRoundKey", f"{timing:.4f}"))
            else:
                self.rounds_tree.insert("", tk.END, values=(f"Round {i}", f"{timing:.4f}"))
    
    def update_stats(self, stats):
        self.stats_text.configure(state="normal")
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, f"Total processing time: {stats['total_time']:.4f} ms\n")
        self.stats_text.insert(tk.END, f"Average round time: {stats['avg_round_time']:.4f} ms\n")
        self.stats_text.insert(tk.END, f"Slowest round: {stats['slowest_round']} ({stats['slowest_time']:.4f} ms)\n")
        self.stats_text.insert(tk.END, f"Fastest round: {stats['fastest_round']} ({stats['fastest_time']:.4f} ms)\n")
        self.stats_text.insert(tk.END, f"File size: {stats['file_size']} bytes\n")
        self.stats_text.insert(tk.END, f"Processing speed: {stats['speed']:.2f} KB/s\n")
        self.stats_text.insert(tk.END, f"Number of blocks: {stats['num_blocks']}\n")
        self.stats_text.insert(tk.END, f"Key length: {stats['key_length']} bytes (AES-{stats['key_length']*8})\n")
        self.stats_text.configure(state="disabled")
