import customtkinter as ctk
from safepaste.config import Config

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, config: Config, on_close_callback=None):
        super().__init__()
        self.config = config
        self.on_close_callback = on_close_callback
        
        self.title("SafePaste - Settings")
        self.geometry("400x300")
        
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.setup_ui()
        
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        
        self.label_title = ctk.CTkLabel(self, text="Settings", font=("Arial", 20, "bold"))
        self.label_title.pack(pady=20)
        
        # Launch on startup
        self.var_startup = ctk.BooleanVar(value=self.config.launch_on_startup)
        self.check_startup = ctk.CTkCheckBox(self, text="Launch on Startup", variable=self.var_startup, command=self.save_settings)
        self.check_startup.pack(pady=10, padx=20, anchor="w")
        
        # Min Text Length
        self.frame_length = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_length.pack(pady=10, padx=20, fill="x")
        
        self.label_length = ctk.CTkLabel(self.frame_length, text="Min Text Length:")
        self.label_length.pack(side="left")
        
        self.entry_length = ctk.CTkEntry(self.frame_length, width=100)
        self.entry_length.pack(side="right")
        self.entry_length.insert(0, str(self.config.min_text_length))
        self.entry_length.bind("<FocusOut>", self.save_settings_event)
        
        # Vault TTL
        self.frame_ttl = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_ttl.pack(pady=10, padx=20, fill="x")
        
        self.label_ttl = ctk.CTkLabel(self.frame_ttl, text="Vault Expiration (sec):")
        self.label_ttl.pack(side="left")
        
        self.entry_ttl = ctk.CTkEntry(self.frame_ttl, width=100)
        self.entry_ttl.pack(side="right")
        self.entry_ttl.insert(0, str(self.config.vault_ttl))
        self.entry_ttl.bind("<FocusOut>", self.save_settings_event)
        
        self.btn_close = ctk.CTkButton(self, text="Close", command=self.on_close)
        self.btn_close.pack(pady=20)

    def save_settings_event(self, event):
        self.save_settings()

    def save_settings(self):
        self.config.launch_on_startup = self.var_startup.get()
        try:
            self.config.min_text_length = int(self.entry_length.get())
        except ValueError:
            pass
        
        try:
            self.config.vault_ttl = int(self.entry_ttl.get())
        except ValueError:
            pass
            
        # TODO: Persist config to disk
        print(f"Settings saved: {self.config}")

    def on_close(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()
