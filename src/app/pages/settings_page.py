import flet as ft
from strings import LANGUAGES
from state import AppState


def build(page: ft.Page) -> ft.Container:
    """Build and return the Settings page with language + theme controls."""

    S = lambda key: LANGUAGES[AppState.lang][key]

    # ── Section header helper ──────────────────────────────────────
    def section_label(text_key):
        return ft.Text(
            LANGUAGES[AppState.lang][text_key],
            size=12, color=ft.Colors.TEAL_300,
            weight=ft.FontWeight.BOLD,
        )

    # ── Language selector ──────────────────────────────────────────
    lang_label = section_label("settings_lang")

    def _lang_btn(code, label_key_tg, label_key_en):
        label = "Tagalog" if code == "TG" else "English"
        is_active = AppState.lang == code

        def on_click(e):
            AppState.set_lang(code)
            page.update()

        return ft.FilledButton(
            content=ft.Text(label, color=ft.Colors.WHITE, size=13),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.TEAL_700 if is_active else ft.Colors.GREY_700,
            ),
            on_click=on_click,
            width=140, height=42,
        )

    lang_tg_btn = _lang_btn("TG", "Tagalog", "Tagalog")
    lang_en_btn = _lang_btn("EN", "English", "English")

    lang_row = ft.Row([lang_tg_btn, lang_en_btn], spacing=12)

    def _refresh_lang_buttons():
        lang_tg_btn.style = ft.ButtonStyle(
            bgcolor=ft.Colors.TEAL_700 if AppState.lang == "TG" else ft.Colors.GREY_700)
        lang_en_btn.style = ft.ButtonStyle(
            bgcolor=ft.Colors.TEAL_700 if AppState.lang == "EN" else ft.Colors.GREY_700)
        lang_label.value = LANGUAGES[AppState.lang]["settings_lang"]
        theme_label.value = LANGUAGES[AppState.lang]["settings_theme"]
        settings_title.value = LANGUAGES[AppState.lang]["settings_title"]
        page.update()

    # ── Theme selector ─────────────────────────────────────────────
    theme_label = section_label("settings_theme")

    THEME_OPTIONS = [
        ("dark",   "settings_theme", "☾ Dark",   ft.Icons.DARK_MODE),
        ("light",  "settings_theme", "☀ Light",  ft.Icons.LIGHT_MODE),
        ("system", "settings_theme", "⊙ System", ft.Icons.SETTINGS_SUGGEST),
    ]

    theme_buttons = {}

    def _apply_theme(mode: str):
        if mode == "dark":
            page.theme_mode = ft.ThemeMode.DARK
        elif mode == "light":
            page.theme_mode = ft.ThemeMode.LIGHT
        else:
            page.theme_mode = ft.ThemeMode.SYSTEM

    def _make_theme_btn(mode, icon, label):
        def on_click(e):
            AppState.set_theme(mode)
            _apply_theme(mode)
            _refresh_theme_buttons()
            page.update()

        btn = ft.FilledButton(
            content=ft.Row(
                [ft.Icon(icon, size=16, color=ft.Colors.WHITE),
                 ft.Text(label, size=12, color=ft.Colors.WHITE)],
                spacing=5, alignment=ft.MainAxisAlignment.CENTER,
            ),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.TEAL_700 if AppState.theme == mode else ft.Colors.GREY_700,
            ),
            on_click=on_click,
            width=100, height=42,
        )
        theme_buttons[mode] = btn
        return btn

    theme_row = ft.Row([
        _make_theme_btn("dark",   ft.Icons.DARK_MODE,       "Dark"),
        _make_theme_btn("light",  ft.Icons.LIGHT_MODE,      "Light"),
        _make_theme_btn("system", ft.Icons.SETTINGS_SUGGEST, "System"),
    ], spacing=10)

    def _refresh_theme_buttons():
        for mode, btn in theme_buttons.items():
            btn.style = ft.ButtonStyle(
                bgcolor=ft.Colors.TEAL_700 if AppState.theme == mode else ft.Colors.GREY_700)

    # ── Title ──────────────────────────────────────────────────────
    settings_title = ft.Text(
        S("settings_title"), size=18, weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER,
    )

    def _setting_card(label_ctrl, control):
        return ft.Container(
            content=ft.Column([label_ctrl, ft.Container(height=6), control], spacing=0),
            bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.WHITE),
            border_radius=16, padding=16,
        )

    container = ft.Container(
        content=ft.Column([
            ft.Container(height=20),
            settings_title,
            ft.Container(height=20),
            ft.Container(
                content=ft.Column([
                    _setting_card(lang_label, lang_row),
                    ft.Container(height=12),
                    _setting_card(theme_label, theme_row),
                ]),
                padding=ft.Padding(left=16, top=0, right=16, bottom=0),
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        expand=True,
    )

    AppState.on_lang_change(_refresh_lang_buttons)

    return container
