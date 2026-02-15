# UI Dashboard interface
import customtkinter as ctk
import pyperclip


def show_dashboard(original, clean):
    ctk.set_appearance_mode("System")

    app = ctk.CTk()
    app.geometry("900x520")
    app.title("SafePaste Review")

    frame = ctk.CTkFrame(app)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    left = ctk.CTkTextbox(frame, width=400)
    left.insert("1.0", original)
    left.configure(state="disabled")
    left.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    right = ctk.CTkTextbox(frame, width=400)
    right.insert("1.0", clean)
    right.configure(state="disabled")
    right.pack(side="right", fill="both", expand=True, padx=5, pady=5)

    def copy_clean():
        pyperclip.copy(clean)
        app.destroy()

    btn = ctk.CTkButton(app, text="Copy Clean", command=copy_clean)
    btn.pack(pady=10)

    app.mainloop()