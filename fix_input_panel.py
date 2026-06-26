import re

with open("ui/input_panel.py", "r") as f:
    content = f.read()

# Replace LinuxSafeOptionMenu class with a custom button that handles the menu
new_menu_class = """class DemoSelectorButton(ctk.CTkButton):
    \"\"\"
    A button that opens a native popup menu for selecting demos.
    This strictly separates the button text (reshaped) from the 
    menu text (raw) to fix BiDi rendering bugs on Linux.
    \"\"\"
    def __init__(self, master, values_map, command, **kwargs):
        super().__init__(master, **kwargs)
        self.values_map = values_map  # dict: {raw_text: index_num}
        self.command = command
        self.bind("<Button-1>", self._show_menu)
        self._last_event = None

    def _show_menu(self, event):
        import tkinter as tk
        self._last_event = event
        
        # Create a native tk.Menu
        menu = tk.Menu(self, tearoff=False, font=FONTS["button"], 
                       bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                       activebackground=COLORS["accent_primary"])
        
        for raw_text, val in self.values_map.items():
            menu.add_command(label=raw_text, command=lambda v=val: self.command(v))
            
        try:
            x = event.x_root
            y = event.y_root
        except Exception:
            x = self.winfo_rootx()
            y = self.winfo_rooty() + self.winfo_height()
            
        menu.tk_popup(x, y)
"""

content = re.sub(r'class LinuxSafeOptionMenu\(ctk\.CTkOptionMenu\):.*?        self\._dropdown_menu\.open\(x, y\)\n\n', new_menu_class + '\n', content, flags=re.DOTALL)

# Replace demo selector creation
old_demo_creation = """        # Demo Selector Dropdown (OptionMenu)
        self._demo_switch = LinuxSafeOptionMenu(
            btn_frame,
            values=[t_raw("demo_safe"), t_raw("demo_deadlock"), t_raw("demo_circular")],
            command=self._on_demo_select,
            height=SIZES["button_height"],
            font=FONTS["button"],
            fg_color=COLORS["bg_input"],
            button_color=COLORS["btn_secondary"],
            button_hover_color=COLORS["btn_secondary_hover"],
            text_color=COLORS["text_primary"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_card_hover"],
            dropdown_text_color=COLORS["text_primary"],
            dropdown_font=FONTS["button"],
        )
        self._demo_switch.set(t("demo_select"))
        self._demo_switch.pack(side="left", padx=(10, 0))"""

new_demo_creation = """        # Demo Selector (Custom Button + Native Menu)
        self._demo_switch = DemoSelectorButton(
            btn_frame,
            text=t("demo_select"),
            values_map={
                t_raw("demo_safe"): 1,
                t_raw("demo_deadlock"): 2,
                t_raw("demo_circular"): 3
            },
            command=self._load_preset,
            height=SIZES["button_height"],
            font=FONTS["button"],
            fg_color=COLORS["btn_secondary"],
            hover_color=COLORS["btn_secondary_hover"],
            text_color=COLORS["text_primary"],
        )
        self._demo_switch.pack(side="left", padx=(10, 0))"""

content = content.replace(old_demo_creation, new_demo_creation)

# Modify refresh_translation for demo switch
old_refresh = """        # Re-populate demo dropdown values
        self._demo_switch.configure(
            values=[t_raw("demo_safe"), t_raw("demo_deadlock"), t_raw("demo_circular")]
        )
        self._demo_switch.set(t("demo_select"))"""

new_refresh = """        # Update demo button text and menu values
        self._demo_switch.configure(text=t("demo_select"))
        self._demo_switch.values_map = {
            t_raw("demo_safe"): 1,
            t_raw("demo_deadlock"): 2,
            t_raw("demo_circular"): 3
        }"""

content = content.replace(old_refresh, new_refresh)

# Modify _on_demo_select
content = re.sub(r'    def _on_demo_select\(self, choice: str\):.*?            self\._load_preset\(3\)\n', '', content, flags=re.DOTALL)

with open("ui/input_panel.py", "w") as f:
    f.write(content)
print("Updated input_panel.py")
