"""Theme configuration for the Deadlock Handler application."""

# ──────────── Color Palette ────────────
COLORS = {
    # Primary gradient
    "bg_dark": "#0f0f1a",
    "bg_main": "#141425",
    "bg_card": "#1c1c35",
    "bg_card_hover": "#24244a",
    "bg_input": "#1a1a30",
    "bg_sidebar": "#12122a",

    # Accent colors
    "accent_primary": "#7c5cfc",
    "accent_secondary": "#5b8dee",
    "accent_gradient_start": "#7c5cfc",
    "accent_gradient_end": "#5b8dee",

    # Status colors
    "success": "#4ade80",
    "success_bg": "#1a3a2a",
    "warning": "#fbbf24",
    "warning_bg": "#3a3420",
    "danger": "#f87171",
    "danger_bg": "#3a1a1a",
    "info": "#60a5fa",
    "info_bg": "#1a2a3a",

    # Text colors
    "text_primary": "#e8e8f0",
    "text_secondary": "#9090b0",
    "text_muted": "#606080",
    "text_bright": "#ffffff",

    # Border & separator
    "border": "#2a2a50",
    "border_active": "#7c5cfc",
    "separator": "#252545",

    # Matrix cell colors
    "cell_alloc": "#3d2b7a",
    "cell_request": "#2b4a7a",
    "cell_available": "#2b7a4a",
    "cell_total": "#4a3a2b",
    "cell_header": "#252550",

    # Process status
    "proc_alive": "#4ade80",
    "proc_waiting": "#fbbf24",
    "proc_dead": "#f87171",

    # Button
    "btn_primary": "#7c5cfc",
    "btn_primary_hover": "#9070ff",
    "btn_secondary": "#2a2a50",
    "btn_secondary_hover": "#3a3a60",
    "btn_danger": "#dc2626",
    "btn_danger_hover": "#ef4444",
}

# ──────────── Fonts ────────────
BASE_FONTS = {
    "heading_lg": ("Segoe UI", 24, "bold"),
    "heading_md": ("Segoe UI", 19, "bold"),
    "heading_sm": ("Segoe UI", 16, "bold"),
    "body": ("Segoe UI", 14),
    "body_sm": ("Segoe UI", 13),
    "mono": ("JetBrains Mono", 14),
    "mono_sm": ("JetBrains Mono", 13),
    "mono_xs": ("JetBrains Mono", 12),
    "label": ("Segoe UI", 13),
    "button": ("Segoe UI", 14, "bold"),
    "sidebar_item": ("Segoe UI", 14),
    "sidebar_active": ("Segoe UI", 14, "bold"),
    "matrix_cell": ("JetBrains Mono", 14),
    "matrix_header": ("JetBrains Mono", 13, "bold"),
    "log_text": ("JetBrains Mono", 14),
}

FONTS = {
    key: (val[0], val[1], val[2]) if len(val) > 2 else (val[0], val[1])
    for key, val in BASE_FONTS.items()
}

def get_scaled_font(font_key: str, scale: float) -> tuple:
    """Return a scaled font tuple based on a local scale."""
    val = BASE_FONTS[font_key]
    family = val[0]
    size = val[1]
    style = val[2] if len(val) > 2 else ""
    scaled_size = max(8, int(size * scale))
    if style:
        return (family, scaled_size, style)
    return (family, scaled_size)

# ──────────── Sizes ────────────
BASE_SIZES = {
    "sidebar_width": 300,
    "corner_radius": 12,
    "corner_radius_sm": 8,
    "padding": 16,
    "padding_sm": 8,
    "padding_xs": 4,
    "entry_height": 38,
    "button_height": 42,
    "matrix_cell_width": 60,
    "matrix_cell_height": 36,
    "scrollbar_width": 6,
}

SIZES = dict(BASE_SIZES)

def get_scaled_size(size_key: str, scale: float) -> int:
    """Return a scaled size based on a local scale."""
    return int(BASE_SIZES[size_key] * scale)

# ──────────── Strategy Definitions ────────────
STRATEGIES = [
    {
        "id": 1,
        "title": "حذف گرفتن و منتظر بودن",
        "subtitle": "Prevention — Hold & Wait",
        "icon": "🛡️",
        "category": "prevention",
    },
    {
        "id": 2,
        "title": "حذف انحصار منابع",
        "subtitle": "Prevention — Mutual Exclusion",
        "icon": "🛡️",
        "category": "prevention",
    },
    {
        "id": 3,
        "title": "حذف انتظار چرخشی",
        "subtitle": "Prevention — Circular Wait",
        "icon": "🛡️",
        "category": "prevention",
    },
    {
        "id": 4,
        "title": "جلوگیری از تخصیص منبع",
        "subtitle": "Avoidance — Banker's Algorithm",
        "icon": "⚠️",
        "category": "avoidance",
    },
    {
        "id": 5,
        "title": "جلوگیری از شروع فرآیند جدید",
        "subtitle": "Avoidance — Process Initiation",
        "icon": "⚠️",
        "category": "avoidance",
    },
    {
        "id": 6,
        "title": "حذف همه فرآیندهای بن‌بست",
        "subtitle": "Detection — Kill All",
        "icon": "🔍",
        "category": "detection",
    },
    {
        "id": 7,
        "title": "حذف بر اساس کمترین زمان سرویس",
        "subtitle": "Detection — Least Service Time",
        "icon": "🔍",
        "category": "detection",
    },
    {
        "id": 8,
        "title": "حذف بر اساس کمترین منابع",
        "subtitle": "Detection — Least Resources",
        "icon": "🔍",
        "category": "detection",
    },
]
