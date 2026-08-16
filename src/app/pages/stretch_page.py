import flet as ft
from strings import LANGUAGES
from state import AppState


def build(page: ft.Page) -> ft.Container:
    """Build and return the stretch exercises page."""

    S = lambda key: LANGUAGES[AppState.lang][key]

    ex_title = ft.Text(S("ex_title"), size=18, weight=ft.FontWeight.BOLD,
                       color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER)
    ex_sub   = ft.Text(S("ex_sub"),   size=12, color=ft.Colors.WHITE54,
                       text_align=ft.TextAlign.CENTER)
    exercise_list = ft.Column(spacing=10)

    def render_exercises():
        exercise_list.controls.clear()
        for ex in LANGUAGES[AppState.lang]["exercises"]:
            card = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(icon=ex["icon"], color=ft.Colors.WHITE, size=28),
                        bgcolor=ft.Colors.TEAL_700, border_radius=12,
                        width=50, height=50, alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column([
                        ft.Text(ex["title"], size=15, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE),
                        ft.Text(ex["steps"], size=11, color=ft.Colors.WHITE70, max_lines=3),
                    ], spacing=3, expand=True),
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                border_radius=15, padding=12,
            )
            exercise_list.controls.append(card)

    render_exercises()

    container = ft.Container(
        content=ft.Column([
            ft.Container(height=20),
            ex_title,
            ex_sub,
            ft.Container(height=15),
            ft.Container(content=exercise_list,
                         padding=ft.Padding(left=15, top=0, right=15, bottom=15)),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
        expand=True,
    )

    def _refresh_lang():
        ex_title.value = LANGUAGES[AppState.lang]["ex_title"]
        ex_sub.value   = LANGUAGES[AppState.lang]["ex_sub"]
        render_exercises()
        page.update()

    AppState.on_lang_change(_refresh_lang)

    return container
