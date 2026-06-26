"""Input panel for setting up processes and resources with language support."""

from __future__ import annotations

from typing import Callable, Optional
import tkinter

import customtkinter as ctk

from models.system_state import SystemState
from .theme import COLORS, FONTS, SIZES, get_scaled_font, get_scaled_size
from .i18n import t, t_raw


class DemoSelectorButton(ctk.CTkButton):
    """
    A button that opens a native popup menu for selecting demos.
    This strictly separates the button text (reshaped) from the 
    menu text (raw) to fix BiDi rendering bugs on Linux.
    """
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
        
        from .i18n import f
        for raw_text, val in self.values_map.items():
            menu.add_command(label=f(raw_text), command=lambda v=val: self.command(v))
            
        try:
            x = event.x_root
            y = event.y_root
        except Exception:
            x = self.winfo_rootx()
            y = self.winfo_rooty() + self.winfo_height()
            
        menu.tk_popup(x, y)


class InputPanel(ctk.CTkFrame):
    """
    Panel for configuring system parameters: number of processes,
    resources, total resources, and individual allocation/request values.
    """

    def __init__(
        self,
        master,
        on_state_changed: Callable[[SystemState], None],
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=SIZES["corner_radius"],
            **kwargs,
        )
        self._on_state_changed = on_state_changed
        self.state = SystemState()

        # Entry tracking
        self._alloc_entries: list[list[ctk.CTkEntry]] = []
        self._req_entries: list[list[ctk.CTkEntry]] = []
        self._total_entries: list[ctk.CTkEntry] = []
        self._svc_entries: list[ctk.CTkEntry] = []
        self._matrix_frame: Optional[ctk.CTkScrollableFrame] = None
        self._zoom_scale = 1.0

        self._build()

    def _build(self):
        # ── Header ──
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 8))

        self._title_lbl = ctk.CTkLabel(
            header,
            text=t("sys_settings"),
            font=FONTS["heading_sm"],
            text_color=COLORS["text_bright"],
            anchor="w",
        )
        self._title_lbl.pack(side="left")

        # Zoom Controls
        self._zoom_in_btn = ctk.CTkButton(
            header, text="➕", width=28, height=28,
            font=("Segoe UI", 12, "bold"),
            fg_color=COLORS["btn_secondary"], hover_color=COLORS["btn_secondary_hover"],
            corner_radius=SIZES["corner_radius_sm"],
            command=self._zoom_in
        )
        self._zoom_in_btn.pack(side="right", padx=2)

        self._zoom_out_btn = ctk.CTkButton(
            header, text="➖", width=28, height=28,
            font=("Segoe UI", 12, "bold"),
            fg_color=COLORS["btn_secondary"], hover_color=COLORS["btn_secondary_hover"],
            corner_radius=SIZES["corner_radius_sm"],
            command=self._zoom_out
        )
        self._zoom_out_btn.pack(side="right", padx=2)

        # ── Config Row ──
        config_frame = ctk.CTkFrame(self, fg_color="transparent")
        config_frame.pack(fill="x", padx=16, pady=(0, 8))

        # Number of processes
        self._proc_lbl = ctk.CTkLabel(
            config_frame,
            text=t("processes"),
            font=FONTS["label"],
            text_color=COLORS["text_secondary"],
        )
        self._proc_lbl.grid(row=0, column=0, padx=(0, 6), sticky="w")

        self._num_proc_var = ctk.StringVar(value="3")
        ctk.CTkEntry(
            config_frame,
            textvariable=self._num_proc_var,
            width=60,
            height=SIZES["entry_height"],
            font=FONTS["mono"],
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            justify="center",
        ).grid(row=0, column=1, padx=(0, 16))

        # Number of resources
        self._res_lbl = ctk.CTkLabel(
            config_frame,
            text=t("resources"),
            font=FONTS["label"],
            text_color=COLORS["text_secondary"],
        )
        self._res_lbl.grid(row=0, column=2, padx=(0, 6), sticky="w")

        self._num_res_var = ctk.StringVar(value="3")
        ctk.CTkEntry(
            config_frame,
            textvariable=self._num_res_var,
            width=60,
            height=SIZES["entry_height"],
            font=FONTS["mono"],
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            justify="center",
        ).grid(row=0, column=3, padx=(0, 16))

        # Buttons
        btn_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=4, padx=(8, 0))

        self._apply_btn = ctk.CTkButton(
            btn_frame,
            text=t("apply"),
            font=FONTS["button"],
            fg_color=COLORS["btn_primary"],
            hover_color=COLORS["btn_primary_hover"],
            height=SIZES["button_height"],
            width=90,
            corner_radius=SIZES["corner_radius_sm"],
            command=self._apply_config,
        )
        self._apply_btn.pack(side="left", padx=(0, 6))

        self._random_btn = ctk.CTkButton(
            btn_frame,
            text=t("random"),
            font=FONTS["button"],
            fg_color=COLORS["btn_secondary"],
            hover_color=COLORS["btn_secondary_hover"],
            text_color=COLORS["text_primary"],
            height=SIZES["button_height"],
            width=90,
            corner_radius=SIZES["corner_radius_sm"],
            command=self._generate_random,
        )
        self._random_btn.pack(side="left")

        # Demo Selector (Custom Button + Native Menu)
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
        self._demo_switch.pack(side="left", padx=(10, 0))

        # ── Matrix container (scrollable) ──
        self._matrix_container = ctk.CTkFrame(self, fg_color="transparent")
        self._matrix_container.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        # Initialize with default values
        self._apply_config()

    def _apply_config(self):
        """Apply configuration and create matrix entries."""
        try:
            n = int(self._num_proc_var.get())
            m = int(self._num_res_var.get())
        except ValueError:
            return

        n = max(1, min(n, 10))
        m = max(1, min(m, 8))

        self._num_proc_var.set(str(n))
        self._num_res_var.set(str(m))

        self.state.initialize(n, m, [5] * m)
        self._rebuild_matrix()

    def _generate_random(self):
        """Generate random system state."""
        try:
            n = int(self._num_proc_var.get())
            m = int(self._num_res_var.get())
        except ValueError:
            return

        n = max(1, min(n, 10))
        m = max(1, min(m, 8))

        self.state.generate_random(n, m, max_resource=8)
        self._num_proc_var.set(str(n))
        self._num_res_var.set(str(m))
        self._rebuild_matrix()
        self._notify()

    def _rebuild_matrix(self):
        """Rebuild the matrix entry grid."""
        # Clear old
        if self._matrix_frame is None:
            frame = ctk.CTkScrollableFrame(
                self._matrix_container,
                fg_color=COLORS["bg_dark"],
                corner_radius=SIZES["corner_radius_sm"],
                scrollbar_button_color=COLORS["bg_card"],
                scrollbar_button_hover_color=COLORS["accent_primary"],
            )
            frame.pack(fill="both", expand=True)
            self._matrix_frame = frame
        else:
            # Safely clear children without destroying the scrollable frame itself
            for child in self._matrix_frame.winfo_children():
                child.destroy()

        self._alloc_entries = []
        self._req_entries = []
        self._total_entries = []
        self._svc_entries = []

        n = self.state.num_processes
        m = self.state.num_resources

        assert self.state.allocation is not None
        assert self.state.request is not None
        assert self.state.total is not None

        scaled_cell_w = get_scaled_size("matrix_cell_width", self._zoom_scale)
        scaled_cell_h = get_scaled_size("matrix_cell_height", self._zoom_scale)
        matrix_header_font = get_scaled_font("matrix_header", self._zoom_scale)
        matrix_cell_font = get_scaled_font("matrix_cell", self._zoom_scale)

        # ── Header Row ──
        # Empty corner cell
        ctk.CTkLabel(
            self._matrix_frame,
            text="",
            width=70,
        ).grid(row=0, column=0)

        # Allocation header
        alloc_start = 1
        for j in range(m):
            col = alloc_start + j
            lbl = ctk.CTkLabel(
                self._matrix_frame,
                text=f"R{j}",
                font=matrix_header_font,
                text_color=COLORS["accent_primary"],
                width=scaled_cell_w,
                height=scaled_cell_h,
                fg_color=COLORS["cell_header"],
                corner_radius=4,
            )
            lbl.grid(row=0, column=col, padx=1, pady=1)

        # Separator label
        sep_col = alloc_start + m
        ctk.CTkLabel(
            self._matrix_frame,
            text="│",
            font=FONTS["mono"],
            text_color=COLORS["border"],
            width=12,
        ).grid(row=0, column=sep_col, rowspan=n + 3)

        # Request header
        req_start = sep_col + 1
        for j in range(m):
            col = req_start + j
            lbl = ctk.CTkLabel(
                self._matrix_frame,
                text=f"R{j}",
                font=matrix_header_font,
                text_color=COLORS["accent_secondary"],
                width=scaled_cell_w,
                height=scaled_cell_h,
                fg_color=COLORS["cell_header"],
                corner_radius=4,
            )
            lbl.grid(row=0, column=col, padx=1, pady=1)

        # Separator
        sep2_col = req_start + m
        ctk.CTkLabel(
            self._matrix_frame,
            text="│",
            font=FONTS["mono"],
            text_color=COLORS["border"],
            width=12,
        ).grid(row=0, column=sep2_col, rowspan=n + 3)

        # Service time header
        svc_col = sep2_col + 1
        self._svc_header_lbl = ctk.CTkLabel(
            self._matrix_frame,
            text=t("svc_time"),
            font=matrix_header_font,
            text_color=COLORS["warning"],
            width=scaled_cell_w + 10,
            height=scaled_cell_h,
            fg_color=COLORS["cell_header"],
            corner_radius=4,
        )
        self._svc_header_lbl.grid(row=0, column=svc_col, padx=1, pady=1)

        # ── Title row ──
        ctk.CTkLabel(
            self._matrix_frame,
            text="",
            width=70,
        ).grid(row=1, column=0)

        # Allocation label spanning
        alloc_label_frame = ctk.CTkFrame(self._matrix_frame, fg_color="transparent")
        alloc_label_frame.grid(row=1, column=alloc_start, columnspan=m, sticky="ew")
        self._alloc_header_lbl = ctk.CTkLabel(
            alloc_label_frame,
            text=t("allocation"),
            font=FONTS["body_sm"],
            text_color=COLORS["accent_primary"],
        )
        self._alloc_header_lbl.pack()

        # Request label spanning
        req_label_frame = ctk.CTkFrame(self._matrix_frame, fg_color="transparent")
        req_label_frame.grid(row=1, column=req_start, columnspan=m, sticky="ew")
        self._req_header_lbl = ctk.CTkLabel(
            req_label_frame,
            text=t("request"),
            font=FONTS["body_sm"],
            text_color=COLORS["accent_secondary"],
        )
        self._req_header_lbl.pack()

        # ── Process rows ──
        for i in range(n):
            row = i + 2

            # Process name
            status_color = COLORS["proc_alive"]
            ctk.CTkLabel(
                self._matrix_frame,
                text=f"  P{i}",
                font=matrix_header_font,
                text_color=status_color,
                width=70,
                height=scaled_cell_h,
                anchor="w",
            ).grid(row=row, column=0, padx=2, pady=1)

            # Allocation entries
            alloc_row_entries = []
            for j in range(m):
                col = alloc_start + j
                var = ctk.StringVar(value=str(int(self.state.allocation[i][j])))
                entry = ctk.CTkEntry(
                    self._matrix_frame,
                    textvariable=var,
                    width=scaled_cell_w,
                    height=scaled_cell_h,
                    font=matrix_cell_font,
                    fg_color=COLORS["cell_alloc"],
                    border_color=COLORS["border"],
                    text_color=COLORS["text_primary"],
                    justify="center",
                    corner_radius=4,
                )
                entry.grid(row=row, column=col, padx=1, pady=1)
                alloc_row_entries.append(entry)
            self._alloc_entries.append(alloc_row_entries)

            # Request entries
            req_row_entries = []
            for j in range(m):
                col = req_start + j
                var = ctk.StringVar(value=str(int(self.state.request[i][j])))
                entry = ctk.CTkEntry(
                    self._matrix_frame,
                    textvariable=var,
                    width=scaled_cell_w,
                    height=scaled_cell_h,
                    font=matrix_cell_font,
                    fg_color=COLORS["cell_request"],
                    border_color=COLORS["border"],
                    text_color=COLORS["text_primary"],
                    justify="center",
                    corner_radius=4,
                )
                entry.grid(row=row, column=col, padx=1, pady=1)
                req_row_entries.append(entry)
            self._req_entries.append(req_row_entries)

            # Service time entry
            svc_var = ctk.StringVar(value=str(self.state.processes[i].service_time))
            svc_entry = ctk.CTkEntry(
                self._matrix_frame,
                textvariable=svc_var,
                width=scaled_cell_w + 10,
                height=scaled_cell_h,
                font=matrix_cell_font,
                fg_color=COLORS["cell_total"],
                border_color=COLORS["border"],
                text_color=COLORS["warning"],
                justify="center",
                corner_radius=4,
            )
            svc_entry.grid(row=row, column=svc_col, padx=1, pady=1)
            self._svc_entries.append(svc_entry)

        # ── Total & Available row ──
        total_row = n + 2

        ctk.CTkFrame(
            self._matrix_frame,
            fg_color=COLORS["separator"],
            height=1,
        ).grid(row=total_row, column=0, columnspan=svc_col + 1, sticky="ew", pady=4)

        total_row += 1

        self._total_row_lbl = ctk.CTkLabel(
            self._matrix_frame,
            text=t("total"),
            font=matrix_header_font,
            text_color=COLORS["text_bright"],
            width=70,
            height=scaled_cell_h,
            anchor="w",
        )
        self._total_row_lbl.grid(row=total_row, column=0, padx=2, pady=1)

        self._total_entries = []
        for j in range(m):
            col = alloc_start + j
            var = ctk.StringVar(value=str(int(self.state.total[j])))
            entry = ctk.CTkEntry(
                self._matrix_frame,
                textvariable=var,
                width=scaled_cell_w,
                height=scaled_cell_h,
                font=matrix_cell_font,
                fg_color=COLORS["cell_available"],
                border_color=COLORS["border"],
                text_color=COLORS["success"],
                justify="center",
                corner_radius=4,
            )
            entry.grid(row=total_row, column=col, padx=1, pady=1)
            self._total_entries.append(entry)

    def read_state(self) -> SystemState:
        """Read current values from entries and update the state."""
        n = self.state.num_processes
        m = self.state.num_resources

        # Read total
        total = []
        for j in range(m):
            try:
                val = int(self._total_entries[j].get())
            except (ValueError, IndexError):
                val = 5
            total.append(max(0, val))

        self.state.initialize(n, m, total)

        # Read allocation & request
        for i in range(n):
            alloc_vals = []
            req_vals = []
            for j in range(m):
                try:
                    a = int(self._alloc_entries[i][j].get())
                except (ValueError, IndexError):
                    a = 0
                try:
                    r = int(self._req_entries[i][j].get())
                except (ValueError, IndexError):
                    r = 0
                alloc_vals.append(max(0, a))
                req_vals.append(max(0, r))

            self.state.set_allocation(i, alloc_vals)
            self.state.set_request(i, req_vals)

        # Read service times
        for i in range(n):
            try:
                svc = float(self._svc_entries[i].get())
            except (ValueError, IndexError):
                svc = 0.0
            self.state.processes[i].service_time = max(0.0, svc)

        return self.state

    def _notify(self):
        """Notify parent of state change."""
        self._on_state_changed(self.read_state())

    def update_display(self, state: SystemState):
        """Update displayed values from a (possibly modified) state."""
        assert state.allocation is not None
        assert state.request is not None

        for i in range(state.num_processes):
            for j in range(state.num_resources):
                if i < len(self._alloc_entries) and j < len(self._alloc_entries[i]):
                    self._alloc_entries[i][j].delete(0, "end")
                    self._alloc_entries[i][j].insert(0, str(int(state.allocation[i][j])))
                if i < len(self._req_entries) and j < len(self._req_entries[i]):
                    self._req_entries[i][j].delete(0, "end")
                    self._req_entries[i][j].insert(0, str(int(state.request[i][j])))


    def _load_preset(self, num: int):
        """Load specific preset state and populate entries."""
        if num == 1:
            n, m = 5, 3
            total = [10, 5, 7]
            self.state.initialize(n, m, total)
            self.state.set_allocation(0, [0, 1, 0])
            self.state.set_allocation(1, [2, 0, 0])
            self.state.set_allocation(2, [3, 0, 2])
            self.state.set_allocation(3, [2, 1, 1])
            self.state.set_allocation(4, [0, 0, 2])

            self.state.set_request(0, [7, 4, 3])
            self.state.set_request(1, [1, 2, 2])
            self.state.set_request(2, [6, 0, 0])
            self.state.set_request(3, [0, 1, 1])
            self.state.set_request(4, [4, 3, 1])

            self.state.processes[0].service_time = 2.5
            self.state.processes[1].service_time = 4.0
            self.state.processes[2].service_time = 1.5
            self.state.processes[3].service_time = 6.2
            self.state.processes[4].service_time = 3.8
        elif num == 2:
            n, m = 3, 3
            total = [7, 2, 6]
            self.state.initialize(n, m, total)
            self.state.set_allocation(0, [2, 0, 0])
            self.state.set_allocation(1, [3, 0, 2])
            self.state.set_allocation(2, [2, 1, 1])

            self.state.set_request(0, [2, 1, 0])
            self.state.set_request(1, [1, 0, 1])
            self.state.set_request(2, [1, 1, 1])

            self.state.processes[0].service_time = 1.0
            self.state.processes[1].service_time = 2.5
            self.state.processes[2].service_time = 5.0
        elif num == 3:
            n, m = 3, 3
            total = [3, 3, 3]
            self.state.initialize(n, m, total)
            self.state.set_allocation(0, [1, 0, 0])
            self.state.set_allocation(1, [0, 1, 0])
            self.state.set_allocation(2, [0, 0, 1])

            self.state.set_request(0, [0, 1, 0])
            self.state.set_request(1, [0, 0, 1])
            self.state.set_request(2, [1, 0, 0])

            self.state.processes[0].service_time = 3.0
            self.state.processes[1].service_time = 3.0
            self.state.processes[2].service_time = 3.0

        self._num_proc_var.set(str(n))
        self._num_res_var.set(str(m))
        self._rebuild_matrix()
        self.update_display(self.state)

        # Populate service time and total entry boxes
        for i in range(n):
            if i < len(self._svc_entries):
                self._svc_entries[i].delete(0, "end")
                self._svc_entries[i].insert(0, str(self.state.processes[i].service_time))
        assert self.state.total is not None
        for j in range(m):
            if j < len(self._total_entries):
                self._total_entries[j].delete(0, "end")
                self._total_entries[j].insert(0, str(int(self.state.total[j])))

        self._demo_switch.configure(text=t("demo_select"))
        self._notify()

    def refresh_translation(self):
        """Update all text labels in the input panel without rebuilding the entire matrix."""
        self._title_lbl.configure(text=t("sys_settings"))
        self._proc_lbl.configure(text=t("processes"))
        self._res_lbl.configure(text=t("resources"))
        self._apply_btn.configure(text=t("apply"))
        self._random_btn.configure(text=t("random"))

        # Update demo button text and menu values
        self._demo_switch.configure(text=t("demo_select"))
        self._demo_switch.values_map = {
            t_raw("demo_safe"): 1,
            t_raw("demo_deadlock"): 2,
            t_raw("demo_circular"): 3
        }

        # Update labels inside matrix frame if it exists
        if self._matrix_frame is not None:
            if hasattr(self, "_alloc_header_lbl") and self._alloc_header_lbl.winfo_exists():
                self._alloc_header_lbl.configure(text=t("allocation"))
            if hasattr(self, "_req_header_lbl") and self._req_header_lbl.winfo_exists():
                self._req_header_lbl.configure(text=t("request"))
            if hasattr(self, "_svc_header_lbl") and self._svc_header_lbl.winfo_exists():
                self._svc_header_lbl.configure(text=t("svc_time"))
            if hasattr(self, "_total_row_lbl") and self._total_row_lbl.winfo_exists():
                self._total_row_lbl.configure(text=t("total"))

    def _zoom_in(self):
        new_scale = round(max(0.7, min(self._zoom_scale + 0.1, 1.7)), 1)
        if new_scale != self._zoom_scale:
            self._zoom_scale = new_scale
            self.refresh_zoom()

    def _zoom_out(self):
        new_scale = round(max(0.7, min(self._zoom_scale - 0.1, 1.7)), 1)
        if new_scale != self._zoom_scale:
            self._zoom_scale = new_scale
            self.refresh_zoom()

    def refresh_zoom(self):
        """Rebuild matrix frame to apply updated size metrics while maintaining values."""
        current_state = self.read_state()
        self._rebuild_matrix()
        self.update_display(current_state)

        # Restore service times and total entries
        for i in range(current_state.num_processes):
            if i < len(self._svc_entries):
                self._svc_entries[i].delete(0, "end")
                self._svc_entries[i].insert(0, str(current_state.processes[i].service_time))
        assert current_state.total is not None
        for j in range(current_state.num_resources):
            if j < len(self._total_entries):
                self._total_entries[j].delete(0, "end")
                self._total_entries[j].insert(0, str(int(current_state.total[j])))
