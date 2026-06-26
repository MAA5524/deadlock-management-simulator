import re

# 1. Fix app.py: Window Title and PanedWindow for top section
with open("ui/app.py", "r") as f:
    app_content = f.read()

# Fix window title to use t_raw
app_content = app_content.replace(
    'self.title(f"{t(\'app_title\')} — {t(\'app_subtitle\')}")',
    'from .i18n import t_raw\n        self.title(f"{t_raw(\'app_title\')} — {t_raw(\'app_subtitle\')}")'
)

# Add top horizontal paned window
top_paned_pattern = re.compile(
    r'(# ── Top section: Input \+ Graph side by side ──\n        top_section = ctk\.CTkFrame\(self\._pw_content, fg_color="transparent"\)\n        self\._pw_content\.add\(top_section, minsize=350\))(.*?)# ── Bottom section: Result panel ──',
    re.DOTALL
)

new_top_paned = r"""\1

        # Use a horizontal PanedWindow inside the top section
        import tkinter as tk
        self._pw_top = tk.PanedWindow(
            top_section,
            orient=tk.HORIZONTAL,
            bg=COLORS["separator"],
            bd=0,
            sashwidth=4,
            sashpad=0,
            showhandle=False,
            sashcursor="sb_h_double_arrow"
        )
        self._pw_top.pack(fill="both", expand=True, padx=12, pady=(12, 6))

        # Input panel (left side of top)
        self._input_panel = InputPanel(
            self._pw_top,
            on_state_changed=self._on_state_changed,
        )
        self._pw_top.add(self._input_panel, minsize=300)

        # Right column: Graph + Action buttons
        right_col = ctk.CTkFrame(self._pw_top, fg_color="transparent")
        self._pw_top.add(right_col, minsize=300)

        # Graph canvas
        self._graph_canvas = GraphCanvas(right_col)
        self._graph_canvas.pack(fill="both", expand=True, pady=(0, 8))

        # Action buttons bar
        action_bar = ctk.CTkFrame(
            right_col,
            fg_color=COLORS["bg_card"],
            corner_radius=SIZES["corner_radius"],
            height=66,
        )
        action_bar.pack(fill="x")
        action_bar.pack_propagate(False)

        action_inner = ctk.CTkFrame(action_bar, fg_color="transparent")
        action_inner.pack(expand=True)

        # Strategy label
        self._strategy_label = ctk.CTkLabel(
            action_inner,
            text=t("strat_not_selected"),
            font=FONTS["body"],
            text_color=COLORS["text_muted"],
        )
        self._strategy_label.pack(side="left", padx=(12, 20))

        # Run button
        self._run_btn = ctk.CTkButton(
            action_inner,
            text=t("run"),
            font=FONTS["button"],
            fg_color=COLORS["btn_primary"],
            hover_color=COLORS["btn_primary_hover"],
            height=40,
            width=120,
            corner_radius=SIZES["corner_radius_sm"],
            command=self._run_strategy,
            state="disabled",
        )
        self._run_btn.pack(side="left", padx=4)

        # Reset button
        self._reset_btn = ctk.CTkButton(
            action_inner,
            text=t("reset"),
            font=FONTS["button"],
            fg_color=COLORS["btn_secondary"],
            hover_color=COLORS["btn_secondary_hover"],
            text_color=COLORS["text_primary"],
            height=40,
            width=100,
            corner_radius=SIZES["corner_radius_sm"],
            command=self._reset,
        )
        self._reset_btn.pack(side="left", padx=4)

        # Detect deadlock button
        self._detect_btn = ctk.CTkButton(
            action_inner,
            text=t("detect"),
            font=FONTS["button"],
            fg_color=COLORS["btn_secondary"],
            hover_color=COLORS["btn_secondary_hover"],
            text_color=COLORS["info"],
            height=40,
            width=110,
            corner_radius=SIZES["corner_radius_sm"],
            command=self._detect_only,
        )
        self._detect_btn.pack(side="left", padx=4)

        # Zoom Out Button
        self._zoom_out_btn = ctk.CTkButton(
            action_inner,
            text="➖",
            width=36,
            height=40,
            font=("Segoe UI", 14, "bold"),
            fg_color=COLORS["btn_secondary"],
            hover_color=COLORS["btn_secondary_hover"],
            corner_radius=SIZES["corner_radius_sm"],
            command=self._zoom_out,
        )
        self._zoom_out_btn.pack(side="left", padx=2)

        # Zoom In Button
        self._zoom_in_btn = ctk.CTkButton(
            action_inner,
            text="➕",
            width=36,
            height=40,
            font=("Segoe UI", 14, "bold"),
            fg_color=COLORS["btn_secondary"],
            hover_color=COLORS["btn_secondary_hover"],
            corner_radius=SIZES["corner_radius_sm"],
            command=self._zoom_in,
        )
        self._zoom_in_btn.pack(side="left", padx=2)

        """
app_content = top_paned_pattern.sub(new_top_paned + r'# ── Bottom section: Result panel ──', app_content)

# Add scroll-to-zoom binds to app_content inside _build_layout
app_content = app_content.replace(
    'self._update_graph()',
    'self._update_graph()\n\n        # Bind Ctrl+MouseWheel for zoom\n        self.bind("<Control-MouseWheel>", self._on_mouse_wheel)\n        self.bind("<Control-Button-4>", self._on_mouse_wheel)  # Linux specific\n        self.bind("<Control-Button-5>", self._on_mouse_wheel)'
)

# Add _on_mouse_wheel method
app_content = app_content.replace(
    '    def _zoom_in(self):',
    '    def _on_mouse_wheel(self, event):\n        """Zoom based on mouse wheel scroll."""\n        # Linux uses event.num (4 up, 5 down)\n        # Windows/Mac uses event.delta (>0 up, <0 down)\n        if hasattr(event, "num") and event.num == 4:\n            self._zoom_in()\n        elif hasattr(event, "num") and event.num == 5:\n            self._zoom_out()\n        elif hasattr(event, "delta") and event.delta > 0:\n            self._zoom_in()\n        elif hasattr(event, "delta") and event.delta < 0:\n            self._zoom_out()\n\n    def _zoom_in(self):'
)


with open("ui/app.py", "w") as f:
    f.write(app_content)
print("Updated app.py")
