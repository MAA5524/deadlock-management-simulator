"""Resource Allocation Graph (RAG) canvas visualization."""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

import customtkinter as ctk

from models.system_state import SystemState
from .theme import COLORS, FONTS, SIZES
from .i18n import t


class GraphCanvas(ctk.CTkFrame):
    """
    Canvas-based Resource Allocation Graph visualization.
    - Circles = Processes
    - Squares = Resources
    - Arrows from Process to Resource = Request
    - Arrows from Resource to Process = Allocation
    """

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            **kwargs,
        )

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 4))

        self._title_lbl = ctk.CTkLabel(
            header,
            text=t("rag_title"),
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

        # Canvas
        self._canvas = ctk.CTkCanvas(
            self,
            bg=COLORS["bg_dark"],
            highlightthickness=0,
        )
        self._canvas.pack(fill="both", expand=True, padx=12, pady=(4, 12))

        self._state: Optional[SystemState] = None
        self._deadlocked: List[int] = []
        self._cycles: List[List[Tuple[str, int, int]]] = []
        self._zoom_scale = 1.0

        # Bind resize
        self._canvas.bind("<Configure>", self._on_resize)

    def _zoom_in(self):
        new_scale = round(max(0.5, min(self._zoom_scale + 0.1, 2.0)), 1)
        if new_scale != self._zoom_scale:
            self._zoom_scale = new_scale
            self._draw_graph()

    def _zoom_out(self):
        new_scale = round(max(0.5, min(self._zoom_scale - 0.1, 2.0)), 1)
        if new_scale != self._zoom_scale:
            self._zoom_scale = new_scale
            self._draw_graph()

    def update_graph(self, state: SystemState, deadlocked: Optional[List[int]] = None, cycles: Optional[List[List[Tuple[str, int, int]]]] = None):
        """Update graph with new state."""
        self._state = state
        self._deadlocked = deadlocked or []
        self._cycles = cycles or []
        self._draw_graph()

    def _on_resize(self, event=None):
        """Redraw on resize."""
        if self._state is not None:
            self._draw_graph()

    def _draw_graph(self):
        """Draw the RAG on the canvas."""
        self._canvas.delete("all")

        if self._state is None:
            return

        w = self._canvas.winfo_width()
        h = self._canvas.winfo_height()

        if w < 50 or h < 50:
            return

        state = self._state
        assert state.total is not None
        assert state.allocation is not None
        assert state.request is not None

        n = state.num_processes
        m = state.num_resources

        # Layout: processes on left, resources on right
        margin = 50
        proc_x = w * 0.28
        res_x = w * 0.72

        proc_positions: List[Tuple[float, float]] = []
        res_positions: List[Tuple[float, float]] = []

        # Calculate positions
        proc_spacing = (h - 2 * margin) / max(n, 1)
        for i in range(n):
            y = margin + proc_spacing * (i + 0.5)
            proc_positions.append((proc_x, y))

        res_spacing = (h - 2 * margin) / max(m, 1)
        for j in range(m):
            y = margin + res_spacing * (j + 0.5)
            res_positions.append((res_x, y))

        # Draw edges first (behind nodes)
        for i in range(n):
            if not state.processes[i].is_alive:
                continue
            px, py = proc_positions[i]
            for j in range(m):
                rx, ry = res_positions[j]

                # Check if this edge is in a cycle
                is_alloc_cycle = any(('alloc', i, j) in c for c in self._cycles)
                is_req_cycle = any(('req', i, j) in c for c in self._cycles)

                # Allocation: Resource → Process (green arrows)
                if state.allocation[i][j] > 0:
                    self._draw_arrow(
                        rx - (20 * self._zoom_scale), ry, px + (22 * self._zoom_scale), py,
                        color=COLORS["danger"] if is_alloc_cycle else COLORS["success"],
                        label=str(int(state.allocation[i][j])),
                        label_color=COLORS["danger"] if is_alloc_cycle else COLORS["success"],
                        is_cycle=is_alloc_cycle,
                    )

                # Request: Process → Resource (red/yellow arrows)
                if state.request[i][j] > 0:
                    is_dl = i in self._deadlocked
                    color = COLORS["danger"] if (is_dl or is_req_cycle) else COLORS["warning"]
                    self._draw_arrow(
                        px + (22 * self._zoom_scale), py, rx - (20 * self._zoom_scale), ry,
                        color=color,
                        label=str(int(state.request[i][j])),
                        label_color=color,
                        dashed=is_dl and not is_req_cycle,
                        is_cycle=is_req_cycle,
                    )

        # Draw process nodes (circles)
        radius = 20 * self._zoom_scale
        for i in range(n):
            px, py = proc_positions[i]
            p = state.processes[i]

            if not p.is_alive:
                fill = COLORS["bg_card"]
                outline = COLORS["text_muted"]
                text_c = COLORS["text_muted"]
            elif i in self._deadlocked:
                fill = COLORS["danger_bg"]
                outline = COLORS["danger"]
                text_c = COLORS["danger"]
            else:
                fill = "#1a1a40"
                outline = COLORS["accent_primary"]
                text_c = COLORS["accent_primary"]

            self._canvas.create_oval(
                px - radius, py - radius,
                px + radius, py + radius,
                fill=fill,
                outline=outline,
                width=2,
            )
            self._canvas.create_text(
                px, py,
                text=p.name,
                fill=text_c,
                font=("Segoe UI", int(14 * self._zoom_scale), "bold"),
            )

        # Draw resource nodes (squares)
        sq = 20 * self._zoom_scale
        for j in range(m):
            rx, ry = res_positions[j]

            self._canvas.create_rectangle(
                rx - sq, ry - sq,
                rx + sq, ry + sq,
                fill="#1a2a40",
                outline=COLORS["accent_secondary"],
                width=2,
            )
            self._canvas.create_text(
                rx, ry - (6 * self._zoom_scale),
                text=state.resources[j].name,
                fill=COLORS["accent_secondary"],
                font=("Segoe UI", int(13 * self._zoom_scale), "bold"),
            )
            self._canvas.create_text(
                rx, ry + (10 * self._zoom_scale),
                text=f"[{int(state.total[j])}]",
                fill=COLORS["text_muted"],
                font=("JetBrains Mono", int(11 * self._zoom_scale)),
            )

        # Legend
        self._draw_legend(w, h)

    def _draw_arrow(
        self,
        x1: float, y1: float,
        x2: float, y2: float,
        color: str,
        label: str = "",
        label_color: str = "",
        dashed: bool = False,
        is_cycle: bool = False,
    ):
        """Draw an arrow with optional label."""
        dash = (6, 4) if dashed else ()

        # Shorten arrow slightly
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx * dx + dy * dy)
        if length < 1:
            return

        width = 3.5 if is_cycle else 1.5

        # Draw line
        self._canvas.create_line(
            x1, y1, x2, y2,
            fill=color,
            width=width,
            arrow="last",
            arrowshape=(10, 12, 5) if not is_cycle else (14, 16, 7),
            dash=dash,
        )

        # Draw label at midpoint
        if label:
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            # Offset label perpendicular to line
            nx = -dy / length * 12
            ny = dx / length * 12
            self._canvas.create_text(
                mx + nx, my + ny,
                text=label,
                fill=label_color or color,
                font=("JetBrains Mono", 12, "bold"),
            )

    def _draw_legend(self, w: float, h: float):
        """Draw a small legend at the bottom."""
        y = h - 20
        x = 16

        items = [
            ("──→", COLORS["success"], t("legend_alloc")),
            ("- - →", COLORS["warning"], t("legend_req")),
            ("- - →", COLORS["danger"], t("legend_dl")),
        ]

        for arrow_text, color, label in items:
            self._canvas.create_text(
                x, y,
                text=arrow_text,
                fill=color,
                font=("JetBrains Mono", 12),
                anchor="w",
            )
            x += 50
            self._canvas.create_text(
                x, y,
                text=label,
                fill=COLORS["text_muted"],
                font=("Segoe UI", 12),
                anchor="w",
            )
            x += 75

    def refresh_translation(self):
        """Refresh title and redraw graph to apply translation on legend."""
        self._title_lbl.configure(text=t("rag_title"))
        self._draw_graph()
