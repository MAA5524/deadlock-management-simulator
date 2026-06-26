"""Performance Comparison Panel to run all algorithms and show stats."""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from models.system_state import SystemState
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
from .theme import COLORS, FONTS
from .i18n import f


class ComparisonPanel(ctk.CTkToplevel):
    def __init__(self, parent, state: SystemState, lang: str = "fa"):
        super().__init__(parent)
        self.parent_window = parent
        self.title("مقایسه الگوریتم‌ها" if lang == "fa" else "Algorithm Comparison")
        self.geometry("900x600")
        self.configure(fg_color=COLORS["bg_main"])
        
        self.system_state = state
        self.lang = lang

        self._build_ui()
        
        # Delay grab_set and analysis to allow the window to render first
        self.after(100, self._delayed_init)

    def _delayed_init(self):
        self.transient(self.parent_window)
        try:
            self.grab_set()
        except Exception:
            pass
        self._run_analysis()

    def _build_ui(self):
        # Title
        title_text = f("نتایج اجرای تمام الگوریتم‌ها روی سیستم فعلی") if self.lang == "fa" else "Results of all algorithms on current system"
        self._title = ctk.CTkLabel(
            self, text=title_text, font=FONTS["heading_lg"], text_color=COLORS["text_primary"]
        )
        self._title.pack(pady=20)

        # Plot frame
        self._plot_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._plot_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def _run_analysis(self):
        strategies = [
            ("M.E. Prev", prevent_mutual_exclusion),
            ("H&W Prev", prevent_hold_and_wait),
            ("Circ Prev", prevent_circular_wait),
            ("Banker's", avoid_by_resource_allocation),
            ("Init Avoid", avoid_by_process_initiation),
            ("Kill All", recover_kill_all),
            ("Kill Time", recover_kill_least_service_time),
            ("Kill Res", recover_kill_least_resources),
        ]

        labels = []
        alive_counts = []
        dl_counts = []

        for name, func in strategies:
            # 1. Duplicate state
            sim_state = self.system_state.deep_copy()
            
            # 2. Run algorithm
            try:
                res_state, _ = func(sim_state, lang=self.lang)
            except Exception:
                res_state = sim_state # Fallback if error

            # 3. Measure
            is_dl, deadlocked, _, _ = detect_deadlock(res_state, lang=self.lang)
            alive = sum(p.is_alive for p in res_state.processes)

            labels.append(name)
            alive_counts.append(alive)
            dl_counts.append(len(deadlocked))

        self._draw_chart(labels, alive_counts, dl_counts)

    def _draw_chart(self, labels, alive_counts, dl_counts):
        # Silence annoying font fallback warnings in terminal
        import logging
        logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)
        
        # Set font family to support Persian characters
        plt.rcParams['font.family'] = ['IRANYekanXVF', 'IRANYekanX', 'Noto Sans Arabic', 'sans-serif']
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Style
        fig.patch.set_facecolor('#1E1E2E')
        ax.set_facecolor('#1E1E2E')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_edgecolor('#45475A')

        x = np.arange(len(labels))
        width = 0.35

        lbl_alive = f('فرآیندهای زنده') if self.lang == 'fa' else 'Alive Processes'
        lbl_dl = f('در بن‌بست') if self.lang == 'fa' else 'Deadlocked'

        ax.bar(x - width/2, alive_counts, width, label=lbl_alive, color='#A6E3A1')
        ax.bar(x + width/2, dl_counts, width, label=lbl_dl, color='#F38BA8')

        lbl_y = f('تعداد') if self.lang == 'fa' else 'Count'
        lbl_title = f('مقایسه وضعیت فرآیندها') if self.lang == 'fa' else 'Algorithm Comparison'

        ax.set_ylabel(lbl_y, color='white')
        ax.set_title(lbl_title, color='white')
        ax.set_xticks(x)
        ax.set_xticklabels([f(l) if self.lang == 'fa' else l for l in labels], rotation=45, ha="right", color='white')
        ax.legend(facecolor='#1E1E2E', labelcolor='white', edgecolor='#45475A')

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self._plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
