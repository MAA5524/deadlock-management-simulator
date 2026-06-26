"""Main application window — Deadlock Handler with language switching."""

from __future__ import annotations

import threading
from typing import Optional

import customtkinter as ctk

from models.system_state import SystemState
from models.simulation import SimulationEngine
from algorithms.prevention import (
    prevent_hold_and_wait,
    prevent_mutual_exclusion,
    prevent_circular_wait,
)
from algorithms.avoidance import (
    avoid_by_resource_allocation,
    avoid_by_process_initiation,
)
from algorithms.recovery import (
    recover_kill_all,
    recover_kill_least_service_time,
    recover_kill_least_resources,
)
from algorithms.detection import detect_deadlock

from .theme import COLORS, FONTS, SIZES, STRATEGIES
from .sidebar import Sidebar
from .input_panel import InputPanel
from .result_panel import ResultPanel
from .graph_canvas import GraphCanvas
from .comparison_panel import ComparisonPanel
from .i18n import t, get_language


class DeadlockApp(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # ── Window Configuration ──
        self.geometry("1400x900")
        self.minsize(1024, 768)
        self.configure(fg_color=COLORS["bg_main"])
        self._update_window_title()

        # Maximize window on startup
        try:
            self.attributes('-zoomed', True)
        except Exception:
            try:
                self.state('zoomed')
            except Exception:
                pass

        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # ── State ──
        self._selected_strategy: Optional[int] = None
        self._current_state: Optional[SystemState] = None
        self._result_state: Optional[SystemState] = None
        self._zoom_scale = 1.0
        self._sim_engine: Optional[SimulationEngine] = None
        self._sim_timer_id: Optional[str] = None

        # ── Layout ──
        self._build_layout()

    def _update_window_title(self):
        """Set window title based on current language."""
        from .i18n import t_raw
        self.title(f"{t_raw('app_title')} — {t_raw('app_subtitle')}")

    def _build_layout(self):
        """Build the main layout with resizable paned windows."""
        import tkinter as tk
        
        # Main container
        self._main_container = ctk.CTkFrame(self, fg_color="transparent")
        self._main_container.pack(fill="both", expand=True)

        # ── Main Horizontal PanedWindow ──
        self._pw_main = tk.PanedWindow(
            self._main_container,
            orient=tk.HORIZONTAL,
            bg=COLORS["separator"],
            bd=0,
            sashwidth=4,
            sashpad=0,
            showhandle=False,
            sashcursor="sb_h_double_arrow"
        )
        self._pw_main.pack(fill="both", expand=True)

        # ── Sidebar ──
        self._sidebar = Sidebar(
            self._pw_main,
            on_strategy_select=self._on_strategy_selected,
            on_language_change=self.change_language,
        )
        self._pw_main.add(self._sidebar, width=SIZES["sidebar_width"], minsize=240)

        # ── Content area (Vertical PanedWindow) ──
        self._pw_content = tk.PanedWindow(
            self._pw_main,
            orient=tk.VERTICAL,
            bg=COLORS["separator"],
            bd=0,
            sashwidth=4,
            sashpad=0,
            showhandle=False,
            sashcursor="sb_v_double_arrow"
        )
        self._pw_main.add(self._pw_content, minsize=600)

        # ── Top section: Input + Graph side by side ──
        top_section = ctk.CTkFrame(self._pw_content, fg_color="transparent")
        self._pw_content.add(top_section, minsize=350)

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

        # Input panel (left side of top)
        self._input_panel = InputPanel(
            self._pw_top,
            on_state_changed=self._on_state_changed,
        )
        self._pw_top.add(self._input_panel, minsize=300)

        # Right column: Graph
        right_col = ctk.CTkFrame(self._pw_top, fg_color="transparent")
        self._pw_top.add(right_col, minsize=300)

        # Graph canvas
        self._graph_canvas = GraphCanvas(right_col)
        self._graph_canvas.pack(fill="both", expand=True, pady=(0, 0))

        # Action buttons bar (moved to top_section to span full width)
        action_bar = ctk.CTkFrame(
            top_section,
            fg_color=COLORS["bg_card"],
            corner_radius=SIZES["corner_radius"],
            height=66,
        )
        # Pack action_bar at the bottom of top_section, and _pw_top will take the remaining space above
        action_bar.pack(fill="x", side="bottom", padx=12, pady=(0, 6))
        
        self._pw_top.pack(fill="both", expand=True, side="top", padx=12, pady=(12, 6))



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

        # Compare Button
        self._compare_btn = ctk.CTkButton(
            action_inner,
            text=t("btn_compare"),
            font=FONTS["button"],
            fg_color=COLORS["btn_secondary"],
            hover_color=COLORS["btn_secondary_hover"],
            text_color="#F9E2AF",
            height=40,
            width=110,
            corner_radius=SIZES["corner_radius_sm"],
            command=self._show_comparison,
        )
        self._compare_btn.pack(side="left", padx=4)

        # Play Simulation Button
        self._play_btn = ctk.CTkButton(
            action_inner,
            text=t("btn_play"),
            font=FONTS["button"],
            fg_color=COLORS["btn_secondary"],
            hover_color=COLORS["btn_secondary_hover"],
            text_color="#A6E3A1",
            height=40,
            width=80,
            corner_radius=SIZES["corner_radius_sm"],
            command=self._toggle_play,
        )
        self._play_btn.pack(side="left", padx=4)

        # Step Simulation Button
        self._step_btn = ctk.CTkButton(
            action_inner,
            text=t("btn_step"),
            font=FONTS["button"],
            fg_color=COLORS["btn_secondary"],
            hover_color=COLORS["btn_secondary_hover"],
            text_color="#89B4FA",
            height=40,
            width=80,
            corner_radius=SIZES["corner_radius_sm"],
            command=self._sim_step,
        )
        self._step_btn.pack(side="left", padx=4)

        # ── Bottom section: Result panel ──
        bottom_section = ctk.CTkFrame(self._pw_content, fg_color="transparent")
        self._pw_content.add(bottom_section, minsize=150, height=300)

        self._result_panel = ResultPanel(bottom_section)
        self._result_panel.pack(fill="both", expand=True, padx=12, pady=(6, 12))

        # ── Status bar ──
        status_bar = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_sidebar"],
            height=28,
            corner_radius=0,
        )
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)

        self._status_label = ctk.CTkLabel(
            status_bar,
            text=f"  {t('ready')}",
            font=FONTS["body_sm"],
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        self._status_label.pack(side="left", padx=8)

        # Initialize graph with default state
        self._update_graph()

        # Set initial paned window sash positions for 50/50 split
        def _set_sashes():
            try:
                w = self._pw_top.winfo_width()
                if w > 100:
                    self._pw_top.sash_place(0, w // 2, 0)
                
                h = self._pw_content.winfo_height()
                if h > 100:
                    self._pw_content.sash_place(0, 0, h // 2)
            except Exception:
                pass
                
        self.after(300, _set_sashes)

    def change_language(self):
        """Update translations for all components when language switcher is clicked."""
        self._update_window_title()
        code = get_language()

        # Update button texts
        self._run_btn.configure(text=t("run"))
        self._reset_btn.configure(text=t("reset"))
        self._detect_btn.configure(text=t("detect"))
        self._compare_btn.configure(text=t("btn_compare"))
        
        play_text = t("btn_pause") if self._sim_timer_id else t("btn_play")
        self._play_btn.configure(text=play_text)
        self._step_btn.configure(text=t("btn_step"))

        if self._selected_strategy is None:
            self._strategy_label.configure(text=t("strat_not_selected"))
        else:
            strat = next(s for s in STRATEGIES if s["id"] == self._selected_strategy)
            title_text = t(f"strat_{self._selected_strategy}_title")
            self._strategy_label.configure(
                text=f"{strat['icon']}  {self._selected_strategy}. {title_text}",
            )

        self._sidebar.refresh_translation()
        self._input_panel.refresh_translation()
        self._result_panel.refresh_translation()
        self._graph_canvas.refresh_translation()

        # Update status
        self._set_status(t("ready"))

    def _on_strategy_selected(self, strategy_id: int):
        """Handle strategy selection from sidebar."""
        self._selected_strategy = strategy_id
        self._run_btn.configure(state="normal")

        strat = next(s for s in STRATEGIES if s["id"] == strategy_id)
        title_text = t(f"strat_{strategy_id}_title")
        self._strategy_label.configure(
            text=f"{strat['icon']}  {strategy_id}. {title_text}",
            text_color=COLORS["text_bright"],
        )
        self._set_status(f"{t('ready')} - Strat {strategy_id}")

    def _on_state_changed(self, state: SystemState):
        """Handle state change from input panel."""
        self._current_state = state
        self._update_graph()

    def _update_graph(self):
        """Update the graph canvas with current state."""
        state = self._input_panel.read_state()
        is_dl, deadlocked, _, cycles = detect_deadlock(state, lang=get_language())
        self._graph_canvas.update_graph(state, deadlocked if is_dl else [], cycles=cycles)

    def _detect_only(self):
        """Run deadlock detection only."""
        state = self._input_panel.read_state()
        valid, msg = state.validate()
        if not valid:
            self._result_panel.display_log([f"❌ {msg}"])
            return

        is_dl, deadlocked, log, cycles = detect_deadlock(state, lang=get_language())
        self._result_panel.display_log(log)
        self._graph_canvas.update_graph(state, deadlocked if is_dl else [], cycles=cycles)

        if is_dl:
            proc_names = ", ".join(state.processes[p].name for p in deadlocked)
            self._set_status(f"🔴 Deadlock: {proc_names}")
        else:
            self._set_status(f"🟢 {t('ready')}")

    def _run_strategy(self):
        """Run the selected strategy."""
        if self._selected_strategy is None:
            return

        state = self._input_panel.read_state()
        valid, msg = state.validate()
        if not valid:
            self._result_panel.display_log([f"❌ {msg}"])
            return

        self._set_status("⏳...")
        self._run_btn.configure(state="disabled")

        # Run in thread to keep UI responsive
        def _execute():
            result_state, log = self._execute_strategy(state)
            # Update UI in main thread
            self.after(0, lambda: self._on_execution_done(result_state, log))

        thread = threading.Thread(target=_execute, daemon=True)
        thread.start()

    def _execute_strategy(self, state: SystemState):
        """Execute the selected strategy and return result."""
        lang = get_language()
        strategy_map = {
            1: lambda s: prevent_hold_and_wait(s, lang=lang),
            2: lambda s: prevent_mutual_exclusion(s, lang=lang),
            3: lambda s: prevent_circular_wait(s, lang=lang),
            4: lambda s: avoid_by_resource_allocation(s, lang=lang),
            5: lambda s: avoid_by_process_initiation(s, lang=lang),
            6: lambda s: recover_kill_all(s, lang=lang),
            7: lambda s: recover_kill_least_service_time(s, lang=lang),
            8: lambda s: recover_kill_least_resources(s, lang=lang),
        }

        if self._selected_strategy is None:
            return state, ["❌ Error: No strategy selected"]

        func = strategy_map.get(self._selected_strategy)
        if func is None:
            return state, [f"❌ Error"]

        return func(state)

    def _on_execution_done(self, result_state: SystemState, log: list):
        """Handle execution completion."""
        self._result_state = result_state
        self._result_panel.display_log(log)

        # Update graph with result
        is_dl, deadlocked, _, cycles = detect_deadlock(result_state, lang=get_language())
        self._graph_canvas.update_graph(result_state, deadlocked if is_dl else [], cycles=cycles)

        self._run_btn.configure(state="normal")
        self._set_status("🟢")

    def _reset(self):
        """Reset to original state."""
        self._result_panel.clear()
        self._result_state = None
        self._update_graph()

        self._set_status("🔄")

    def _set_status(self, text: str):
        """Update status bar text."""
        self._status_label.configure(text=f"  {text}")

    def _on_mouse_wheel(self, event):
        pass



    # --- Simulation & Comparison Logic ---

    def _show_comparison(self):
        state = self._input_panel.read_state()
        valid, msg = state.validate()
        if not valid:
            self._result_panel.display_log([f"❌ {msg}"])
            return
        self._comparison_window = ComparisonPanel(self, state, lang=get_language())

    def _toggle_play(self):
        if self._sim_timer_id is not None:
            # Pause
            self.after_cancel(self._sim_timer_id)
            self._sim_timer_id = None
            self._play_btn.configure(text=t("btn_play"))
        else:
            # Play
            if self._sim_engine is None or self._sim_engine.is_finished:
                # Initialize new simulation
                state = self._input_panel.read_state()
                valid, msg = state.validate()
                if not valid:
                    self._result_panel.display_log([f"❌ {msg}"])
                    return
                self._sim_engine = SimulationEngine(state)
                self._result_panel.display_log([])
            
            self._play_btn.configure(text=t("btn_pause"))
            self._sim_tick()

    def _sim_step(self):
        if self._sim_timer_id is not None:
            self._toggle_play() # Pause first if playing
            
        if self._sim_engine is None or self._sim_engine.is_finished:
            state = self._input_panel.read_state()
            valid, msg = state.validate()
            if not valid:
                self._result_panel.display_log([f"❌ {msg}"])
                return
            self._sim_engine = SimulationEngine(state)
            self._result_panel.display_log([])
            
        self._sim_tick(auto_schedule=False)

    def _sim_tick(self, auto_schedule=True):
        if self._sim_engine is None:
            return

        is_running, logs = self._sim_engine.step(lang=get_language())
        
        # Append logs directly without re-reading and re-rendering old logs
        for line in logs:
            self._result_panel.append_log(line)

        # Update UI graph to show simulation state
        state = self._sim_engine.state
        is_dl, deadlocked, _, cycles = detect_deadlock(state, lang=get_language())
        self._graph_canvas.update_graph(state, deadlocked if is_dl else [], cycles=cycles)

        if is_running and auto_schedule:
            self._sim_timer_id = self.after(1500, self._sim_tick)
        elif not is_running:
            if self._sim_timer_id is not None:
                self.after_cancel(self._sim_timer_id)
                self._sim_timer_id = None
            self._play_btn.configure(text=t("btn_play"))
