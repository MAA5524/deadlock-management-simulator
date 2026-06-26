import tkinter as tk
import customtkinter as ctk

app = ctk.CTk()
app.geometry("800x600")
ctk.set_appearance_mode("dark")

# Horizontal PanedWindow (Sidebar | Content)
pw_h = tk.PanedWindow(app, orient=tk.HORIZONTAL, bg="#111111", bd=0, sashwidth=4, sashpad=0, showhandle=False)
pw_h.pack(fill=tk.BOTH, expand=True)

sidebar = ctk.CTkFrame(pw_h, fg_color="#1E1E1E")
ctk.CTkLabel(sidebar, text="Sidebar").pack(pady=20)
pw_h.add(sidebar, width=200, minsize=100)

# Vertical PanedWindow (Top Content | Bottom Result)
pw_v = tk.PanedWindow(pw_h, orient=tk.VERTICAL, bg="#111111", bd=0, sashwidth=4, sashpad=0, showhandle=False)
pw_h.add(pw_v, minsize=400)

top_content = ctk.CTkFrame(pw_v, fg_color="#2D2D2D")
ctk.CTkLabel(top_content, text="Top Content (Input & Graph)").pack(pady=20)
pw_v.add(top_content, minsize=200)

bottom_content = ctk.CTkFrame(pw_v, fg_color="#1E1E1E")
ctk.CTkLabel(bottom_content, text="Bottom Content (Result)").pack(pady=20)
pw_v.add(bottom_content, minsize=100)

app.mainloop()
