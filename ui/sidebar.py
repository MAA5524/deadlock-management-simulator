"""Sidebar component with strategy selection and language switching."""

from __future__ import annotations

from typing import Callable, Optional

import customtkinter as ctk

from .theme import COLORS, FONTS, SIZES, STRATEGIES
from .i18n import t, get_language, set_language


class Sidebar(ctk.CTkFrame):
    """
    Left sidebar with strategy selection grouped by category.
    """

    def __init__(
        self,
        master,
        on_strategy_select: Callable[[int], None],
        on_language_change: Callable[[], None],
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=COLORS["bg_sidebar"],
            corner_radius=0,
            width=SIZES["sidebar_width"],
            **kwargs,
        )
        self.pack_propagate(False)
        self._on_select = on_strategy_select
        self._on_language_change = on_language_change
        self._selected_id: Optional[int] = None
        self._buttons: dict[int, ctk.CTkButton] = {}
        self._cat_labels: list[tuple[ctk.CTkLabel, str]] = []

        self._build()

    def _build(self):
        # ── Title ──
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(24, 4))

        self._title_lbl = ctk.CTkLabel(
            title_frame,
            text=t("app_title"),
            font=FONTS["heading_md"],
            text_color=COLORS["text_bright"],
            anchor="w",
        )
        self._title_lbl.pack(fill="x")

        self._subtitle_lbl = ctk.CTkLabel(
            title_frame,
            text=t("app_subtitle"),
            font=FONTS["body_sm"],
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        self._subtitle_lbl.pack(fill="x", pady=(2, 0))

        # Language Switcher
        lang_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        lang_frame.pack(fill="x", pady=(12, 0))

        self._lang_switch = ctk.CTkSegmentedButton(
            lang_frame,
            values=["FA", "EN"],
            command=self._on_lang_switch_clicked,
            height=28,
            font=FONTS["body_sm"],
            selected_color=COLORS["accent_primary"],
            selected_hover_color=COLORS["btn_primary_hover"],
            fg_color=COLORS["bg_input"],
        )
        self._lang_switch.pack(fill="x")
        self._lang_switch.set("FA" if get_language() == "fa" else "EN")

        # ── Separator ──
        ctk.CTkFrame(
            self, fg_color=COLORS["separator"], height=1, corner_radius=0
        ).pack(fill="x", padx=16, pady=(16, 12))

        # ── Scrollable strategies ──
        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["bg_card"],
            scrollbar_button_hover_color=COLORS["accent_primary"],
        )
        scroll.pack(fill="both", expand=True, padx=8, pady=4)

        categories = [
            ("cat_prevention", "prevention"),
            ("cat_avoidance", "avoidance"),
            ("cat_detection", "detection"),
        ]

        for cat_key, cat_value in categories:
            # Category header
            lbl = ctk.CTkLabel(
                scroll,
                text=t(cat_key),
                font=FONTS["heading_sm"],
                text_color=COLORS["accent_secondary"],
                anchor="w",
            )
            lbl.pack(fill="x", padx=8, pady=(12, 4))
            self._cat_labels.append((lbl, cat_key))

            # Strategy buttons
            for strat in STRATEGIES:
                if strat["category"] != cat_value:
                    continue
                btn = self._create_strategy_button(scroll, strat)
                self._buttons[strat["id"]] = btn

        # ── Bottom info ──
        ctk.CTkFrame(
            self, fg_color=COLORS["separator"], height=1, corner_radius=0
        ).pack(fill="x", padx=16, pady=(8, 0))

        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=(12, 20))

        self._info_lbl = ctk.CTkLabel(
            info_frame,
            text=t("course_title"),
            font=FONTS["body_sm"],
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        self._info_lbl.pack(fill="x")

    def _create_strategy_button(self, parent, strat: dict) -> ctk.CTkButton:
        """Create a styled strategy selection button."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=4, pady=2)

        strat_id = strat["id"]
        btn = ctk.CTkButton(
            frame,
            text=f"  {strat_id}. {t(f'strat_{strat_id}_title')}",
            font=FONTS["sidebar_item"],
            text_color=COLORS["text_secondary"],
            fg_color="transparent",
            hover_color=COLORS["bg_card_hover"],
            anchor="w",
            height=42,
            corner_radius=SIZES["corner_radius_sm"],
            command=lambda sid=strat_id: self._select(sid),
        )
        btn.pack(fill="x")

        return btn

    def _select(self, strategy_id: int):
        """Handle strategy selection."""
        # Deselect previous
        if self._selected_id is not None and self._selected_id in self._buttons:
            self._buttons[self._selected_id].configure(
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
                font=FONTS["sidebar_item"],
            )

        # Select new
        self._selected_id = strategy_id
        if strategy_id in self._buttons:
            self._buttons[strategy_id].configure(
                fg_color=COLORS["accent_primary"],
                text_color=COLORS["text_bright"],
                font=FONTS["sidebar_active"],
            )

        self._on_select(strategy_id)

    def _on_lang_switch_clicked(self, val: str):
        """Handle language switch segmented button click."""
        set_language("fa" if val == "FA" else "en")
        self._on_language_change()

    def refresh_translation(self):
        """Update all text values in the sidebar."""
        self._title_lbl.configure(text=t("app_title"))
        self._subtitle_lbl.configure(text=t("app_subtitle"))

        for lbl, cat_key in self._cat_labels:
            lbl.configure(text=t(cat_key))

        for strat_id, btn in self._buttons.items():
            # Keep bold font if it is selected
            btn.configure(
                text=f"  {strat_id}. {t(f'strat_{strat_id}_title')}"
            )

        self._info_lbl.configure(text=t("course_title"))

    @property
    def selected_strategy(self) -> Optional[int]:
        return self._selected_id
