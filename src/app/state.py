"""
Shared mutable app state.
All pages import this module and read/write the same instance.
"""

class AppState:
    lang: str = "TG"          # Current language code
    theme: str = "dark"       # "dark" | "light" | "system"

    # Live posture data (updated by the db-checker thread)
    slouch_count: int = 0
    slouch_seconds: int = 0
    posture_status: str = "CONNECTING"  # "CONNECTING" | "GOOD" | "SLOUCHING"

    # Callbacks registered by pages so they can re-render when state changes
    _on_lang_change_callbacks: list = []
    _on_theme_change_callbacks: list = []
    _on_posture_change_callbacks: list = []

    @classmethod
    def on_lang_change(cls, fn):
        cls._on_lang_change_callbacks.append(fn)

    @classmethod
    def on_theme_change(cls, fn):
        cls._on_theme_change_callbacks.append(fn)

    @classmethod
    def on_posture_change(cls, fn):
        cls._on_posture_change_callbacks.append(fn)

    @classmethod
    def set_lang(cls, lang: str):
        cls.lang = lang
        for fn in cls._on_lang_change_callbacks:
            fn()

    @classmethod
    def set_theme(cls, theme: str):
        cls.theme = theme
        for fn in cls._on_theme_change_callbacks:
            fn()

    @classmethod
    def set_posture(cls, status: str, count: int, seconds: int):
        cls.posture_status = status
        cls.slouch_count = count
        cls.slouch_seconds = seconds
        for fn in cls._on_posture_change_callbacks:
            fn()
