import os
import time
from tkinter import filedialog, messagebox
from crypto.benchmarked_aes import BenchmarkedAES as AES
from views.encryption_view import EncryptionView

class EncryptionController:
    def __init__(self, view: EncryptionView, main_controller):
        self.view = view
        self.main_controller = main_controller
        self.file_path = None
        self.cipher = None
        
        self.view.set_browse_command(self.browse_file)
        self.view.set_encrypt_command(lambda: self.process_file("encrypt"))
        self.view.set_decrypt_command(lambda: self.process_file("decrypt"))

    def browse_file(self, file_path = None):
        if file_path:
            filename = str(file_path)
        else:
            filename = filedialog.askopenfilename(title="Select a file")        

        if filename or file_path:
            self.file_path = filename
            self.view.update_file_display(filename)
            
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.view.set_input_text(content)
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {str(e)}")

    def process_file(self, operation):
        if not self.file_path:
            messagebox.showerror("Error", "Please select a file first")
            return

        key = self.view.get_encryption_key()
        if not key:
            messagebox.showerror("Error", "Please enter an encryption key")
            return

        key_valid = self._check_key(key)

        if not key_valid:
            messagebox.showerror("Error", "Key must be 16, 24 or 32 bytes long")
            return

        try:
            self.cipher = AES(key)
            
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            start_time = time.perf_counter()
            
            if operation == "encrypt":
                processed_content = self.cipher.encrypt(content)
                extension = ".encrypted"
                success_msg = "Encryption"
            else:
                processed_content = self.cipher.decrypt(content)
                extension = ".decrypted"
                success_msg = "Decryption"

            total_time = (time.perf_counter() - start_time) * 1000
            output_path = os.path.splitext(self.file_path)[0] + extension
            
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(processed_content)

            self.view.set_output_text(processed_content)
            self._update_benchmark_data(total_time)
            messagebox.showinfo("Success", f"{success_msg} completed!\nSaved to: {output_path}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def _check_key(self, key):
        key_size = len(key.encode('utf-8'))
        return (key_size == 16) or (key_size == 24) or (key_size == 32)

    def _update_benchmark_data(self, total_time):
        round_timings = self.cipher.get_round_timings()
        file_size = os.path.getsize(self.file_path)
        num_blocks = self.cipher.get_block_count()
        
        stats = {
            'total_time': total_time,
            'avg_round_time': sum(round_timings) / len(round_timings) if round_timings else 0,
            'slowest_round': round_timings.index(max(round_timings)) if round_timings else 0,
            'slowest_time': max(round_timings) if round_timings else 0,
            'fastest_round': round_timings.index(min(round_timings)) if round_timings else 0,
            'fastest_time': min(round_timings) if round_timings else 0,
            'file_size': file_size,
            'speed': (file_size / 1024) / (total_time / 1000) if total_time > 0 else 0,
            'num_blocks': num_blocks,
            'key_length': len(self.cipher.key)
        }

        self.view.update_round_timings(round_timings)
        self.view.update_stats(stats)