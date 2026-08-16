import flet as ft
import requests
import threading
import time
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# ── Ensure src/app is on sys.path so page modules import cleanly ──
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

ROOT_DIR = APP_DIR.parent.parent
load_dotenv(ROOT_DIR / ".env")
FIREBASE_URL = os.getenv("DATABASE_URL")

from state import AppState
from strings import LANGUAGES
from pages import home_page, stretch_page, settings_page


def main(page: ft.Page):
    page.title        = "Posture Companion"
    page.window.width  = 380
    page.window.height = 750
    page.bgcolor       = "#0F172A"  # deep navy-dark, never changes
    page.padding       = 0
    page.theme_mode    = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme_seed="teal",
        color_scheme=ft.ColorScheme(
            surface="#1E293B",
            primary="#2DD4BF",
        ),
    )

    # ── Build pages once ───────────────────────────────────────────
    home     = home_page.build(page)
    stretch  = stretch_page.build(page)
    settings = settings_page.build(page)

    content_area = ft.Container(content=home, expand=True)

    # ── Navigation bar ─────────────────────────────────────────────
    S = lambda key: LANGUAGES[AppState.lang][key]

    nav_bar = ft.NavigationBar(
        selected_index=0,
        bgcolor="#1E293B",
        indicator_color="#0D9488",
        shadow_color=ft.Colors.BLACK,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.MONITOR_HEART_OUTLINED,
                selected_icon=ft.Icons.MONITOR_HEART,
                label=S("nav_monitor"),
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SELF_IMPROVEMENT,
                selected_icon=ft.Icons.SELF_IMPROVEMENT,
                label=S("nav_exercises"),
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label=S("nav_settings"),
            ),
        ],
    )

    def on_nav_change(e):
        idx = e.control.selected_index
        if idx == 0:
            content_area.content = home
        elif idx == 1:
            content_area.content = stretch
        else:
            content_area.content = settings
        page.update()

    nav_bar.on_change = on_nav_change

    # Update nav labels when language changes
    def _refresh_nav():
        nav_bar.destinations[0].label = LANGUAGES[AppState.lang]["nav_monitor"]
        nav_bar.destinations[1].label = LANGUAGES[AppState.lang]["nav_exercises"]
        nav_bar.destinations[2].label = LANGUAGES[AppState.lang]["nav_settings"]
        page.update()

    # Update theme_mode when theme changes
    def _refresh_theme():
        mode_map = {
            "dark":   ft.ThemeMode.DARK,
            "light":  ft.ThemeMode.LIGHT,
            "system": ft.ThemeMode.SYSTEM,
        }
        page.theme_mode = mode_map.get(AppState.theme, ft.ThemeMode.DARK)
        page.update()

    AppState.on_lang_change(_refresh_nav)
    AppState.on_theme_change(_refresh_theme)

    page.add(ft.Column([content_area, nav_bar], expand=True, spacing=0))

    # ── Firebase poller (background thread) ───────────────────────
    def poll_database():
        while True:
            try:
                response = requests.get(FIREBASE_URL, timeout=5)
                data = response.json()
                if data and "status" in data:
                    AppState.set_posture(
                        status  = data.get("status", "CONNECTING"),
                        count   = data.get("slouch_count", 0),
                        seconds = int(data.get("total_slouch_seconds", 0)),
                    )
            except Exception:
                pass
            time.sleep(1)

    threading.Thread(target=poll_database, daemon=True).start()


if __name__ == "__main__":
    ft.run(main)