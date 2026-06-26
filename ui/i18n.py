"""Internationalization and Persian text reshaping support."""

from __future__ import annotations

import arabic_reshaper
from bidi.algorithm import get_display

# Current language state: 'fa' (Persian) or 'en' (English)
_current_lang = "fa"


def set_language(lang: str):
    """Set the current active language ('fa' or 'en')."""
    global _current_lang
    if lang in ("fa", "en"):
        _current_lang = lang


def get_language() -> str:
    """Get the current active language."""
    return _current_lang


def f(text: str) -> str:
    """
    Format and reshape Persian text for correct RTL display in Tkinter/Canvas.
    If the current language is English, returns the text as-is.
    If the current language is Persian, reshapes Arabic/Persian letters
    and applies BiDi algorithm.
    """
    if not text:
        return ""

    # Only apply reshaping if there are Persian characters
    if any(ord(c) >= 0x0600 and ord(c) <= 0x06FF for c in text):
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            if isinstance(bidi_text, bytes):
                return bidi_text.decode("utf-8")
            return bidi_text
        except Exception:
            return text
    return text


# Translations database
TRANSLATIONS = {
    # ── Sidebar ──
    "app_title": {
        "fa": "مدیریت بن‌بست 🔒",
        "en": "Deadlock Handler 🔒",
    },
    "app_subtitle": {
        "fa": "سیستم مقابله با بن‌بست",
        "en": "Deadlock Handling System",
    },
    "cat_prevention": {
        "fa": "پیشگیری  Prevention 🛡️",
        "en": "🛡️ Prevention",
    },
    "cat_avoidance": {
        "fa": "اجتناب  Avoidance ⚠️",
        "en": "⚠️ Avoidance",
    },
    "cat_detection": {
        "fa": "تشخیص  Detection 🔍",
        "en": "🔍 Detection",
    },
    "course_title": {
        "fa": "پروژه سیستم عامل",
        "en": "Operating Systems Project",
    },

    # ── Strategies ──
    "strat_1_title": {
        "fa": "حذف گرفتن و منتظر بودن",
        "en": "1. Remove Hold & Wait",
    },
    "strat_2_title": {
        "fa": "حذف انحصار منابع",
        "en": "2. Remove Mutual Exclusion",
    },
    "strat_3_title": {
        "fa": "حذف انتظار چرخشی",
        "en": "3. Remove Circular Wait",
    },
    "strat_4_title": {
        "fa": "جلوگیری از تخصیص منبع",
        "en": "4. Avoidance - Banker's Algorithm",
    },
    "strat_5_title": {
        "fa": "جلوگیری از شروع فرآیند جدید",
        "en": "5. Avoidance - Process Initiation",
    },
    "strat_6_title": {
        "fa": "حذف همه فرآیندهای بن‌بست",
        "en": "6. Recovery - Kill All Deadlocked",
    },
    "strat_7_title": {
        "fa": "حذف بر اساس کمترین زمان سرویس",
        "en": "7. Recovery - Least Service Time",
    },
    "strat_8_title": {
        "fa": "حذف بر اساس کمترین منابع",
        "en": "8. Recovery - Least Resources Needed",
    },

    # ── Settings / Input Panel ──
    "sys_settings": {
        "fa": "⚙️ تنظیمات سیستم",
        "en": "⚙️ System Config",
    },
    "processes": {
        "fa": "فرآیندها:",
        "en": "Processes:",
    },
    "resources": {
        "fa": "منابع:",
        "en": "Resources:",
    },
    "apply": {
        "fa": "📝 اعمال",
        "en": "📝 Apply",
    },
    "random": {
        "fa": "🎲 تصادفی",
        "en": "🎲 Random",
    },
    "allocation": {
        "fa": "تخصیص (Allocation)",
        "en": "Allocation",
    },
    "request": {
        "fa": "درخواست (Request)",
        "en": "Request",
    },
    "total": {
        "fa": "  کل (Total)",
        "en": "  Total",
    },
    "svc_time": {
        "fa": "سرویس (s)",
        "en": "Svc (s)",
    },
    "btn_compare": {
        "fa": "📊 مقایسه",
        "en": "📊 Compare",
    },
    "btn_play": {
        "fa": "▶ پخش",
        "en": "▶ Play",
    },
    "btn_pause": {
        "fa": "⏸ توقف",
        "en": "⏸ Pause",
    },
    "btn_step": {
        "fa": "⏭ گام",
        "en": "⏭ Step",
    },

    # ── RAG Canvas ──
    "rag_title": {
        "fa": "📊 گراف تخصیص منابع (RAG)",
        "en": "📊 Resource Allocation Graph (RAG)",
    },
    "legend_alloc": {
        "fa": "تخصیص",
        "en": "Allocation",
    },
    "legend_req": {
        "fa": "درخواست",
        "en": "Request",
    },
    "legend_dl": {
        "fa": "بن‌بست",
        "en": "Deadlock",
    },

    # ── Action Buttons ──
    "run": {
        "fa": "▶  اجرا",
        "en": "▶  Run",
    },
    "reset": {
        "fa": "🔄 ریست",
        "en": "🔄 Reset",
    },
    "detect": {
        "fa": "🔍 تشخیص",
        "en": "🔍 Detect",
    },
    "strat_not_selected": {
        "fa": "استراتژی انتخاب نشده است",
        "en": "Strategy not selected",
    },

    # ── Result Panel ──
    "result_title": {
        "fa": "📋 نتیجه اجرا",
        "en": "📋 Execution Result",
    },
    "clear_log": {
        "fa": "پاک کردن",
        "en": "Clear",
    },
    "ready": {
        "fa": "آماده",
        "en": "Ready",
    },

    # ── Welcomes ──
    "welcome_1": {
        "fa": "یک استراتژی از پنل سمت چپ انتخاب کنید و دکمه «▶ اجرا» را بزنید.",
        "en": "Select a strategy from the sidebar and click '▶ Run'.",
    },
    "welcome_2": {
        "fa": "① ابتدا مقادیر ماتریس‌ها را وارد کنید",
        "en": "1. Enter matrix values first.",
    },
    "welcome_3": {
        "fa": "② یا از دکمه «🎲 تصادفی» استفاده کنید",
        "en": "2. Or use the 'Random' button to pre-fill.",
    },
    "welcome_4": {
        "fa": "③ سپس استراتژی مورد نظر را انتخاب و اجرا کنید",
        "en": "3. Then choose and execute a deadlock handling strategy.",
    },
    "demo_select": {
        "fa": "انتخاب دمو 📋",
        "en": "Select Demo 📋",
    },
    "demo_safe": {
        "fa": "دمو ۱: حالت امن",
        "en": "Demo 1: Safe State",
    },
    "demo_deadlock": {
        "fa": "دمو ۲: حالت بن‌بست",
        "en": "Demo 2: Deadlock State",
    },
    "demo_circular": {
        "fa": "دمو ۳: انتظار چرخشی",
        "en": "Demo 3: Circular Wait",
    },
}


def t(key: str) -> str:
    """Translate a key to current language and format/reshape it."""
    lang = get_language()
    dict_val = TRANSLATIONS.get(key, {})
    val = dict_val.get(lang, dict_val.get("en", key))

    if lang == "fa":
        return f(val)
    return val

def t_raw(key: str) -> str:
    """Translate a key to current language without reshaping (for native widgets)."""
    lang = get_language()
    dict_val = TRANSLATIONS.get(key, {})
    return dict_val.get(lang, dict_val.get("en", key))
