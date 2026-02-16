import customtkinter as ctk
import pyperclip
from typing import Callable

class ReviewWindow(ctk.CTkToplevel):
    def __init__(self, original_text: str, scrubbed_text: str, on_copy: Callable, on_close: Callable):
        super().__init__()
        
        self.original_text = original_text
        self.scrubbed_text = scrubbed_text
        self.on_copy_callback = on_copy
        self.on_close_callback = on_close
        
        self.title("SafePaste - Review PII Detection")
        self.geometry("800x600")
        
        # Make window modal-like (keep on top)
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.setup_ui()
        
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        self.label_header = ctk.CTkLabel(self, text="PII Detected! Review Redactions", font=("Arial", 20, "bold"))
        self.label_header.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Panels
        self.frame_original = ctk.CTkFrame(self)
        self.frame_original.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.label_original = ctk.CTkLabel(self.frame_original, text="Original Text", font=("Arial", 14, "bold"))
        self.label_original.pack(pady=5)
        
        self.text_original = ctk.CTkTextbox(self.frame_original, wrap="word")
        self.text_original.pack(expand=True, fill="both", padx=5, pady=5)
        self.text_original.insert("0.0", self.original_text)
        self.text_original.configure(state="disabled") # Read-only
        
        self.frame_scrubbed = ctk.CTkFrame(self)
        self.frame_scrubbed.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        self.label_scrubbed = ctk.CTkLabel(self.frame_scrubbed, text="Scrubbed Text", font=("Arial", 14, "bold"))
        self.label_scrubbed.pack(pady=5)
        
        self.text_scrubbed = ctk.CTkTextbox(self.frame_scrubbed, wrap="word")
        self.text_scrubbed.pack(expand=True, fill="both", padx=5, pady=5)
        self.text_scrubbed.insert("0.0", self.scrubbed_text) # Editable if user wants manual tweaks? PRD says toggle.
        
        # PRD Requirement: List detected items with checkboxes.
        # For MVP, we'll keep it simple: just show text. 
        # Future: Add sidebar with checkboxes to toggle replacements in scrubbing logic.
        
        # Buttons
        self.frame_buttons = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_buttons.grid(row=2, column=0, columnspan=2, pady=20)
        
        self.btn_cancel = ctk.CTkButton(self.frame_buttons, text="Cancel (Esc)", command=self.on_close, fg_color="gray")
        self.btn_cancel.pack(side="left", padx=20)
        
        self.btn_copy = ctk.CTkButton(self.frame_buttons, text="Copy Clean Text", command=self.on_copy, fg_color="green")
        self.btn_copy.pack(side="left", padx=20)
        
        self.bind("<Escape>", lambda e: self.on_close())
        self.bind("<Return>", lambda e: self.on_copy())

    def on_copy(self):
        # Allow user to edit scrubbed text before copying? 
        # Ideally yes. So detected text should be from the textbox.
        final_text = self.text_scrubbed.get("0.0", "end").strip()
        pyperclip.copy(final_text)
        if self.on_copy_callback:
            self.on_copy_callback(final_text)
        self.destroy()

    def on_close(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()
