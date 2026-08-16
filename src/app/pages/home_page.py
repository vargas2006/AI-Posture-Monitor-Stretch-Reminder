import flet as ft
import sys
import subprocess
from pathlib import Path
from strings import LANGUAGES
from state import AppState

# home_page.py is at: src/app/pages/home_page.py
# so .parent x4 = project root (c:\pypj)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent


def build(page: ft.Page) -> ft.Container:
    """Build and return the home page container."""

    S = lambda key: LANGUAGES[AppState.lang][key]

    # ── Status circle ──────────────────────────────────────────────
    status_icon = ft.Icon(icon=ft.Icons.WIFI_FIND, size=88, color=ft.Colors.WHITE70)
    status_text = ft.Text(
        S("connecting"), size=22, weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER,
    )
    sub_status = ft.Text(
        S("wait_desktop"), size=12, color=ft.Colors.WHITE38,
        text_align=ft.TextAlign.CENTER,
    )

    # Glow ring behind the circle (decorative)
    status_circle = ft.Container(
        content=ft.Column(
            [status_icon, status_text, sub_status],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6,
        ),
        width=265, height=265, border_radius=133,
        bgcolor="#1E2A2A",  # default neutral dark
        alignment=ft.Alignment(0, 0),
        border=ft.Border(
            left=ft.BorderSide(2, "#2DD4BF"),
            right=ft.BorderSide(2, "#2DD4BF"),
            top=ft.BorderSide(2, "#2DD4BF"),
            bottom=ft.BorderSide(2, "#2DD4BF"),
        ),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=30, color="#552DD4BF"),
    )

    # ── Stats cards ────────────────────────────────────────────────
    slouch_count_val = ft.Text("0", size=28, weight=ft.FontWeight.BOLD, color="#FBBF24")
    slouch_count_lbl = ft.Text(S("slouch_count"), size=11, color=ft.Colors.WHITE38)
    slouch_time_val  = ft.Text("0", size=28, weight=ft.FontWeight.BOLD, color="#F87171")
    slouch_time_lbl  = ft.Text(S("slouch_sec"),   size=11, color=ft.Colors.WHITE38)

    def _stat_card(icon, hex_color, val_ctrl, lbl_ctrl):
        return ft.Container(
            content=ft.Column(
                [ft.Icon(icon, color=hex_color, size=20), val_ctrl, lbl_ctrl],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2,
            ),
            bgcolor="#1E293B",
            border_radius=16,
            border=ft.Border(
                left=ft.BorderSide(1, "#334155"),
                right=ft.BorderSide(1, "#334155"),
                top=ft.BorderSide(1, "#334155"),
                bottom=ft.BorderSide(1, "#334155"),
            ),
            padding=16, expand=True,
        )

    stats_row = ft.Row([
        _stat_card(ft.Icons.REPEAT, "#FBBF24", slouch_count_val, slouch_count_lbl),
        _stat_card(ft.Icons.TIMER,  "#F87171", slouch_time_val,  slouch_time_lbl),
    ], spacing=12)

    # ── Camera launcher button ─────────────────────────────────────
    def launch_camera(e):
        script = ROOT_DIR / "src" / "monitor" / "posture_monitor.py"
        subprocess.Popen([sys.executable, str(script), "--lang", AppState.lang])

    btn_text = ft.Text(S("btn_start_cam"), color=ft.Colors.WHITE, size=13,
                       weight=ft.FontWeight.W_500)
    btn_launch = ft.FilledButton(
        content=ft.Row(
            [ft.Icon(ft.Icons.VIDEOCAM_ROUNDED, color=ft.Colors.WHITE, size=18), btn_text],
            alignment=ft.MainAxisAlignment.CENTER, spacing=8,
        ),
        style=ft.ButtonStyle(bgcolor="#0D9488"),
        on_click=launch_camera,
        width=245, height=46,
    )

    # ── Root container ─────────────────────────────────────────────
    container = ft.Container(
        content=ft.Column([
            ft.Container(height=20),
            ft.Text(
                "POSTURE COMPANION", size=17, weight=ft.FontWeight.BOLD,
                color="#94A3B8", text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(height=14),
            ft.Row([status_circle], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
            ft.Container(
                content=stats_row,
                padding=ft.Padding(left=20, top=0, right=20, bottom=0),
            ),
            ft.Container(height=14),
            ft.Row([btn_launch], alignment=ft.MainAxisAlignment.CENTER),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        expand=True,
    )

    # ── Reactive updates ───────────────────────────────────────────
    # Color palettes per status (circle bg, border, shadow, icon color)
    STATUS_COLORS = {
        "GOOD": {
            "bg": "#0F2E1F", "border": "#22C55E",
            "shadow": "#4422C55E", "icon_color": "#86EFAC",
            "icon": ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED,
        },
        "SLOUCHING": {
            "bg": "#2E0F0F", "border": "#EF4444",
            "shadow": "#44EF4444", "icon_color": "#FCA5A5",
            "icon": ft.Icons.WARNING_AMBER_ROUNDED,
        },
        "CONNECTING": {
            "bg": "#1E2A2A", "border": "#2DD4BF",
            "shadow": "#552DD4BF", "icon_color": "#99A3A4",
            "icon": ft.Icons.WIFI_FIND,
        },
    }

    def _apply_status(st):
        c = STATUS_COLORS.get(st, STATUS_COLORS["CONNECTING"])
        status_circle.bgcolor = c["bg"]
        status_circle.border = ft.Border(
            left=ft.BorderSide(2, c["border"]),
            right=ft.BorderSide(2, c["border"]),
            top=ft.BorderSide(2, c["border"]),
            bottom=ft.BorderSide(2, c["border"]),
        )
        status_circle.shadow = ft.BoxShadow(
            spread_radius=1, blur_radius=30, color=c["shadow"])
        status_icon.icon  = c["icon"]
        status_icon.color = c["icon_color"]

    def _refresh_lang():
        S2 = lambda key: LANGUAGES[AppState.lang][key]
        btn_text.value         = S2("btn_start_cam")
        slouch_count_lbl.value = S2("slouch_count")
        slouch_time_lbl.value  = S2("slouch_sec")
        st = AppState.posture_status
        if st == "GOOD":
            status_text.value = S2("good_posture")
            sub_status.value  = S2("good_sub")
        elif st == "SLOUCHING":
            status_text.value = S2("bad_posture")
            sub_status.value  = S2("bad_sub")
        else:
            status_text.value = S2("connecting")
            sub_status.value  = S2("wait_desktop")

    def _refresh_posture():
        st = AppState.posture_status
        slouch_count_val.value = str(AppState.slouch_count)
        slouch_time_val.value  = str(AppState.slouch_seconds)
        S2 = lambda key: LANGUAGES[AppState.lang][key]
        _apply_status(st)
        if st == "GOOD":
            status_text.value = S2("good_posture")
            sub_status.value  = S2("good_sub")
        elif st == "SLOUCHING":
            status_text.value = S2("bad_posture")
            sub_status.value  = S2("bad_sub")
        page.update()

    AppState.on_lang_change(_refresh_lang)
    AppState.on_posture_change(_refresh_posture)

    return container
