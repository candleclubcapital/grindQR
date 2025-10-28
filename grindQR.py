import tkinter as tk
from tkinter import filedialog, ttk
import subprocess
import json
import qrcode
import os
import threading
import base58
from datetime import datetime
from PIL import Image, ImageTk
import time

# Setup output folder
os.makedirs("qrcodes", exist_ok=True)

class GrindQRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("grindQR - Solana Vanity Key Generator")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0a0e27')
        
        # Stats tracking
        self.keys_generated = 0
        self.session_start = datetime.now()
        self.grinding_active = False
        
        self.setup_styles()
        self.create_ui()
        self.log_message("System initialized", "SUCCESS")
        self.log_message(f"Output directory: {os.path.abspath('qrcodes')}", "INFO")
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom colors
        bg_dark = '#0a0e27'
        bg_medium = '#151b3d'
        bg_light = '#1e2749'
        accent = '#00d9ff'
        accent_dim = '#0099cc'
        text_color = '#e0e0e0'
        
        style.configure('Cyber.TFrame', background=bg_dark)
        style.configure('CyberPanel.TFrame', background=bg_medium, relief='flat')
        style.configure('Cyber.TLabel', background=bg_medium, foreground=text_color, 
                       font=('Consolas', 10))
        style.configure('CyberTitle.TLabel', background=bg_dark, foreground=accent,
                       font=('Consolas', 16, 'bold'))
        style.configure('Stats.TLabel', background=bg_dark, foreground=accent,
                       font=('Consolas', 11, 'bold'))
        
        style.configure('Cyber.TEntry', fieldbackground=bg_light, foreground=text_color,
                       insertcolor=accent, borderwidth=1)
        style.configure('Cyber.TButton', background=accent_dim, foreground='#ffffff',
                       borderwidth=0, font=('Consolas', 10, 'bold'))
        style.map('Cyber.TButton', background=[('active', accent)])
        
        style.configure('Cyber.TCheckbutton', background=bg_medium, foreground=text_color,
                       font=('Consolas', 10))
        style.map('Cyber.TCheckbutton', background=[('active', bg_medium)])
        
    def create_ui(self):
        # Main container
        main_container = ttk.Frame(self.root, style='Cyber.TFrame')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_frame = ttk.Frame(main_container, style='Cyber.TFrame')
        title_frame.pack(fill='x', pady=(0, 10))
        
        title = ttk.Label(title_frame, text="⬢ GRINDQR ⬢ SOLANA VANITY GENERATOR", 
                         style='CyberTitle.TLabel')
        title.pack()
        
        # Stats bar
        self.create_stats_bar(main_container)
        
        # Main content area (split)
        content_frame = ttk.Frame(main_container, style='Cyber.TFrame')
        content_frame.pack(fill='both', expand=True)
        
        # Left panel
        left_panel = ttk.Frame(content_frame, style='Cyber.TFrame')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Controls
        self.create_grinder_controls(left_panel)
        self.create_file_picker(left_panel)
        
        # Console
        self.create_console(left_panel)
        
        # Right panel - QR Display
        right_panel = ttk.Frame(content_frame, style='CyberPanel.TFrame')
        right_panel.pack(side='right', fill='both', padx=(5, 0))
        
        self.create_qr_display(right_panel)
        
    def create_stats_bar(self, parent):
        stats_frame = ttk.Frame(parent, style='Cyber.TFrame')
        stats_frame.pack(fill='x', pady=(0, 10))
        
        self.stats_keys = ttk.Label(stats_frame, text="KEYS: 0", style='Stats.TLabel')
        self.stats_keys.pack(side='left', padx=10)
        
        self.stats_status = ttk.Label(stats_frame, text="STATUS: IDLE", style='Stats.TLabel')
        self.stats_status.pack(side='left', padx=10)
        
        self.stats_session = ttk.Label(stats_frame, text="SESSION: 00:00:00", 
                                       style='Stats.TLabel')
        self.stats_session.pack(side='right', padx=10)
        
        self.update_session_timer()
        
    def create_grinder_controls(self, parent):
        frame = ttk.LabelFrame(parent, text=" ◆ VANITY GRINDER ◆ ", style='CyberPanel.TFrame')
        frame.pack(fill='x', pady=(0, 10), padx=2)
        
        # Grid layout
        ttk.Label(frame, text="Starts With:", style='Cyber.TLabel').grid(
            row=0, column=0, padx=10, pady=8, sticky='e')
        self.vanity_start_entry = ttk.Entry(frame, width=30, style='Cyber.TEntry')
        self.vanity_start_entry.grid(row=0, column=1, padx=5, pady=8, sticky='w')
        
        self.ends_with_var = tk.BooleanVar()
        ends_check = ttk.Checkbutton(frame, text="Ends With:", variable=self.ends_with_var,
                                     style='Cyber.TCheckbutton')
        ends_check.grid(row=1, column=0, padx=10, pady=8, sticky='e')
        self.vanity_end_entry = ttk.Entry(frame, width=30, style='Cyber.TEntry')
        self.vanity_end_entry.grid(row=1, column=1, padx=5, pady=8, sticky='w')
        
        self.ignore_case_var = tk.BooleanVar()
        ignore_check = ttk.Checkbutton(frame, text="Ignore Case", 
                                       variable=self.ignore_case_var,
                                       style='Cyber.TCheckbutton')
        ignore_check.grid(row=2, column=0, padx=10, pady=8, sticky='e')
        
        ttk.Label(frame, text="Quantity:", style='Cyber.TLabel').grid(
            row=3, column=0, padx=10, pady=8, sticky='e')
        self.quantity_entry = ttk.Entry(frame, width=10, style='Cyber.TEntry')
        self.quantity_entry.grid(row=3, column=1, padx=5, pady=8, sticky='w')
        self.quantity_entry.insert(0, "1")
        
        # Buttons
        btn_frame = ttk.Frame(frame, style='CyberPanel.TFrame')
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        self.grind_button = ttk.Button(btn_frame, text="▶ START GRINDING", 
                                       command=self.grind_keys, style='Cyber.TButton')
        self.grind_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(btn_frame, text="■ STOP", 
                                      command=self.stop_grinding, style='Cyber.TButton',
                                      state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
    def create_file_picker(self, parent):
        frame = ttk.LabelFrame(parent, text=" ◆ EXISTING KEYPAIR QR EXPORT ◆ ", 
                              style='CyberPanel.TFrame')
        frame.pack(fill='x', pady=(0, 10), padx=2)
        
        inner = ttk.Frame(frame, style='CyberPanel.TFrame')
        inner.pack(fill='x', padx=10, pady=10)
        
        self.keypair_path_entry = ttk.Entry(inner, width=50, style='Cyber.TEntry')
        self.keypair_path_entry.pack(side='left', padx=(0, 10), fill='x', expand=True)
        
        browse_btn = ttk.Button(inner, text="📁 BROWSE", command=self.select_keyfile,
                               style='Cyber.TButton')
        browse_btn.pack(side='left')
        
    def create_console(self, parent):
        frame = ttk.LabelFrame(parent, text=" ◆ SYSTEM CONSOLE ◆ ", 
                              style='CyberPanel.TFrame')
        frame.pack(fill='both', expand=True, padx=2)
        
        # Console text with custom colors
        self.console_log = tk.Text(frame, height=15, bg='#000000', fg='#00ff00',
                                   font=('Consolas', 9), insertbackground='#00ff00',
                                   selectbackground='#003300', relief='flat',
                                   wrap='word')
        self.console_log.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Configure tags for different log levels
        self.console_log.tag_config('INFO', foreground='#00d9ff')
        self.console_log.tag_config('SUCCESS', foreground='#00ff00')
        self.console_log.tag_config('WARNING', foreground='#ffaa00')
        self.console_log.tag_config('ERROR', foreground='#ff0000')
        self.console_log.tag_config('TIMESTAMP', foreground='#888888')
        
        scrollbar = ttk.Scrollbar(frame, command=self.console_log.yview)
        self.console_log.configure(yscrollcommand=scrollbar.set)
        
    def create_qr_display(self, parent):
        ttk.Label(parent, text="◆ QR CODE VIEWER ◆", style='CyberTitle.TLabel',
                 font=('Consolas', 12, 'bold')).pack(pady=10)
        
        # QR display area
        self.qr_frame = ttk.Frame(parent, style='CyberPanel.TFrame')
        self.qr_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.qr_label = ttk.Label(self.qr_frame, text="No QR code generated yet",
                                  style='Cyber.TLabel', anchor='center')
        self.qr_label.pack(expand=True)
        
        # Key info display
        self.key_info_frame = ttk.Frame(parent, style='CyberPanel.TFrame')
        self.key_info_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(self.key_info_frame, text="Public Key:", style='Cyber.TLabel').pack(anchor='w')
        self.pubkey_display = tk.Text(self.key_info_frame, height=2, bg='#1e2749',
                                      fg='#00d9ff', font=('Consolas', 8), wrap='word',
                                      relief='flat')
        self.pubkey_display.pack(fill='x', pady=(2, 10))
        
        ttk.Label(self.key_info_frame, text="Private Key (Base58):", 
                 style='Cyber.TLabel').pack(anchor='w')
        self.privkey_display = tk.Text(self.key_info_frame, height=3, bg='#1e2749',
                                       fg='#ffaa00', font=('Consolas', 8), wrap='word',
                                       relief='flat')
        self.privkey_display.pack(fill='x', pady=2)
        
    def log_message(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.console_log.insert(tk.END, f"[{timestamp}] ", 'TIMESTAMP')
        self.console_log.insert(tk.END, f"[{level}] ", level)
        self.console_log.insert(tk.END, f"{message}\n")
        self.console_log.see(tk.END)
        
    def update_stats(self):
        self.stats_keys.config(text=f"KEYS: {self.keys_generated}")
        status = "GRINDING..." if self.grinding_active else "IDLE"
        self.stats_status.config(text=f"STATUS: {status}")
        
    def update_session_timer(self):
        elapsed = datetime.now() - self.session_start
        hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        self.stats_session.config(text=f"SESSION: {hours:02d}:{minutes:02d}:{seconds:02d}")
        self.root.after(1000, self.update_session_timer)
        
    def display_qr(self, qr_path, public_key, private_key_base58):
        try:
            # Load and display QR
            img = Image.open(qr_path)
            img = img.resize((300, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.qr_label.configure(image=photo, text="")
            self.qr_label.image = photo
            
            # Display key info
            self.pubkey_display.delete('1.0', tk.END)
            self.pubkey_display.insert('1.0', public_key)
            
            self.privkey_display.delete('1.0', tk.END)
            self.privkey_display.insert('1.0', private_key_base58)
            
            # Force window update to display immediately
            self.root.update_idletasks()
            
            self.log_message(f"QR code displayed for key: {public_key[:8]}...{public_key[-8:]}", 
                           "SUCCESS")
        except Exception as e:
            self.log_message(f"Failed to display QR: {str(e)}", "ERROR")
            
    def extract_phantom_key(self, filepath):
        self.log_message(f"Reading keypair from: {filepath}", "INFO")
        with open(filepath, 'r') as f:
            key_data = json.load(f)
        full_key_bytes = bytes(key_data)
        private_key_base58 = base58.b58encode(full_key_bytes).decode()
        self.log_message(f"Successfully extracted {len(full_key_bytes)} byte keypair", "SUCCESS")
        return private_key_base58
        
    def generate_qr(self, private_key_base58, filename_prefix, public_key=None):
        self.log_message(f"Generating QR code for: {filename_prefix}", "INFO")
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(private_key_base58)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        
        filename = os.path.join("qrcodes", f"{filename_prefix}.png")
        img.save(filename)
        self.log_message(f"QR saved: {os.path.abspath(filename)}", "SUCCESS")
        self.log_message(f"Private key length: {len(private_key_base58)} characters", "INFO")
        
        # Immediately display the QR (use after_idle for thread safety)
        self.root.after_idle(lambda: self.display_qr(filename, public_key or filename_prefix, 
                                                      private_key_base58))
        
        self.keys_generated += 1
        self.update_stats()
        
    def select_keyfile(self):
        filepath = filedialog.askopenfilename(
            title="Select Solana Keypair File",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if not filepath:
            return
            
        self.keypair_path_entry.delete(0, tk.END)
        self.keypair_path_entry.insert(0, filepath)
        
        try:
            self.log_message("=== KEYPAIR IMPORT INITIATED ===", "INFO")
            private_key_base58 = self.extract_phantom_key(filepath)
            filename_prefix = os.path.splitext(os.path.basename(filepath))[0]
            self.generate_qr(private_key_base58, filename_prefix)
            self.log_message("=== IMPORT COMPLETE ===", "SUCCESS")
        except Exception as e:
            self.log_message(f"Import failed: {str(e)}", "ERROR")
            
    def stop_grinding(self):
        self.grinding_active = False
        self.grind_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.log_message("Grinding stopped by user", "WARNING")
        self.update_stats()
        
    def grind_keys(self):
        def worker():
            self.grinding_active = True
            self.grind_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.update_stats()
            
            vanity_start = self.vanity_start_entry.get()
            vanity_end = self.vanity_end_entry.get() if self.ends_with_var.get() else ''
            ignore_case_flag = '--ignore-case' if self.ignore_case_var.get() else ''
            quantity = self.quantity_entry.get()
            
            self.log_message("=== GRINDING SESSION INITIATED ===", "INFO")
            self.log_message(f"Parameters: starts={vanity_start or 'none'}, "
                           f"ends={vanity_end or 'none'}, "
                           f"ignore_case={self.ignore_case_var.get()}, "
                           f"quantity={quantity}", "INFO")
            
            starts_with_option = f"--starts-with {vanity_start}:{quantity}" if vanity_start else ''
            ends_with_option = f"--ends-with {vanity_end}:{quantity}" if vanity_end else ''
            
            command = f"solana-keygen grind {ignore_case_flag} {starts_with_option} {ends_with_option}"
            self.log_message(f"Executing: {command}", "INFO")
            
            try:
                process = subprocess.Popen(
                    command, shell=True, stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT, text=True
                )
                
                public_key = None
                keyfile_path = None
                
                for line in process.stdout:
                    if not self.grinding_active:
                        process.terminate()
                        break
                        
                    line = line.strip()
                    if line:
                        self.log_message(f"OUTPUT: {line}", "INFO")
                    
                    # Check for public key pattern
                    if "Found matching key" in line or "Wrote public key to" in line:
                        # Try to extract public key from the line
                        parts = line.split()
                        for i, part in enumerate(parts):
                            # Solana addresses are base58 and typically 32-44 chars
                            if len(part) >= 32 and len(part) <= 44:
                                public_key = part
                                self.log_message(f"✓ Public key detected: {public_key}", "SUCCESS")
                                break
                    
                    # Check for keypair file
                    if "Wrote keypair to" in line or ".json" in line:
                        # Extract file path - it's usually after "to" or the .json file itself
                        if "Wrote keypair to" in line:
                            keyfile_path = line.split("Wrote keypair to")[1].strip()
                        else:
                            # Look for .json in the line
                            parts = line.split()
                            for part in parts:
                                if ".json" in part:
                                    keyfile_path = part.strip()
                                    break
                        
                        if keyfile_path:
                            self.log_message(f"Keypair file detected: {keyfile_path}", "SUCCESS")
                            self.log_message(f"DEBUG: public_key={public_key}, keyfile_path={keyfile_path}", "INFO")
                            
                            # Generate QR immediately when we have the file
                            if keyfile_path:
                                try:
                                    self.log_message("=== AUTO-GENERATING QR CODE ===", "INFO")
                                    private_key_base58 = self.extract_phantom_key(keyfile_path)
                                    # Use public key from file name if we don't have it
                                    if not public_key:
                                        public_key = os.path.splitext(os.path.basename(keyfile_path))[0]
                                    self.generate_qr(private_key_base58, public_key, public_key)
                                    self.log_message("QR code automatically generated and displayed!", "SUCCESS")
                                except Exception as e:
                                    self.log_message(f"QR generation failed: {str(e)}", "ERROR")
                                    import traceback
                                    self.log_message(f"Traceback: {traceback.format_exc()}", "ERROR")
                                public_key = None
                                keyfile_path = None
                        
                self.log_message("=== GRINDING SESSION COMPLETE ===", "SUCCESS")
                
            except Exception as e:
                self.log_message(f"Grinding error: {str(e)}", "ERROR")
            finally:
                self.grinding_active = False
                self.grind_button.config(state='normal')
                self.stop_button.config(state='disabled')
                self.update_stats()
                
        threading.Thread(target=worker, daemon=True).start()

# Run application
if __name__ == "__main__":
    root = tk.Tk()
    app = GrindQRApp(root)
    root.mainloop()
