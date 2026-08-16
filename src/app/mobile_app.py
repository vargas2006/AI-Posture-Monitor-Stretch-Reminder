import flet as ft
import requests
import time
import threading
import os
from pathlib import Path
from dotenv import load_dotenv

# Path to the root directory
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / '.env')
FIREBASE_URL = os.getenv("DATABASE_URL")

# --- MGA STRETCHING EXERCISES ---
STRETCH_EXERCISES = [
    {
        "title": "Neck Roll",
        "icon": ft.Icons.SELF_IMPROVEMENT,
        "steps": "Dahan-dahang ikutin ang ulo mo pakanan, pababa, pakaliwa, at pataas. 5 beses sa bawat direksyon."
    },
    {
        "title": "Shoulder Shrug",
        "icon": ft.Icons.FITNESS_CENTER,
        "steps": "Itaas ang dalawang balikat mo papunta sa tenga. Hawakan ng 5 seconds. Ibaba. Ulitin 10 beses."
    },
    {
        "title": "Cat-Cow Stretch",
        "icon": ft.Icons.PETS,
        "steps": "Umupo nang tuwid. Paikutin ang likod mo paharap (parang pusa), tapos paikutin palikod. 10 beses."
    },
    {
        "title": "Chest Opener",
        "icon": ft.Icons.OPEN_WITH,
        "steps": "Pagdikitin ang dalawang kamay mo sa likod. Itaas nang dahan-dahan. Hawakan ng 15 seconds."
    },
    {
        "title": "Side Stretch",
        "icon": ft.Icons.SWAP_HORIZ,
        "steps": "Itaas ang kanang kamay at dumantay pakaliwa. Hawakan ng 10 seconds. Palitan ng kabilang side."
    },
]

def main(page: ft.Page):
    # --- PAGE SETTINGS ---
    page.title = "Posture Companion"
    page.window.width = 380
    page.window.height = 750
    page.bgcolor = ft.Colors.GREY_900
    page.padding = 0
    
    # --- STATE VARIABLES ---
    current_slouch_count = 0
    current_slouch_seconds = 0
    
    # ================================================================
    # HOME PAGE (Ang Main Screen)
    # ================================================================
    
    # Status Icon (Malaking icon sa gitna)
    status_icon = ft.Icon(
        icon=ft.Icons.WIFI_FIND,
        size=100,
        color=ft.Colors.WHITE,
    )
    
    # Status Text
    status_text = ft.Text(
        "Kumokonekta...",
        size=26,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE,
        text_align=ft.TextAlign.CENTER,
    )
    
    # Sub-status (Extra message)
    sub_status = ft.Text(
        "Hintayin ang Desktop App",
        size=14,
        color=ft.Colors.WHITE54,
        text_align=ft.TextAlign.CENTER,
    )
    
    # Status Container (Ang malaking bilog na nagbabago ng kulay)
    status_container = ft.Container(
        content=ft.Column(
            [status_icon, status_text, sub_status],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        width=280,
        height=280,
        border_radius=140,
        bgcolor=ft.Colors.BLUE_GREY_800,
        alignment=ft.Alignment(0, 0),
        shadow=ft.BoxShadow(
            spread_radius=2,
            blur_radius=20,
            color=ft.Colors.BLACK38,
        ),
    )
    
    # --- STATISTICS CARDS ---
    slouch_count_text = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER)
    slouch_time_text = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_300)
    
    stats_row = ft.Row(
        [
            # Slouch Count Card
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(icon=ft.Icons.REPEAT, color=ft.Colors.AMBER, size=24),
                        slouch_count_text,
                        ft.Text("Slouch Count", size=11, color=ft.Colors.WHITE54),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
                bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE),
                border_radius=15,
                padding=15,
                expand=True,
            ),
            # Slouch Time Card
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(icon=ft.Icons.TIMER, color=ft.Colors.RED_300, size=24),
                        slouch_time_text,
                        ft.Text("Slouch Seconds", size=11, color=ft.Colors.WHITE54),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
                bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE),
                border_radius=15,
                padding=15,
                expand=True,
            ),
        ],
        spacing=10,
    )
    
    # --- HOME PAGE LAYOUT ---
    home_page = ft.Container(
        content=ft.Column(
            [
                ft.Container(height=30),
                # Title Bar
                ft.Text(
                    "POSTURE COMPANION",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=20),
                # Big Status Circle
                ft.Row([status_container], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=25),
                # Stats Cards
                ft.Container(content=stats_row, padding=ft.Padding(left=20, top=0, right=20, bottom=0)),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )
    
    # ================================================================
    # STRETCH PAGE (Ang Exercises Screen)
    # ================================================================
    
    exercise_list = ft.Column(spacing=10)
    
    for ex in STRETCH_EXERCISES:
        card = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icon=ex["icon"], color=ft.Colors.WHITE, size=30),
                        bgcolor=ft.Colors.TEAL_700,
                        border_radius=12,
                        width=50,
                        height=50,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column(
                        [
                            ft.Text(ex["title"], size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text(ex["steps"], size=11, color=ft.Colors.WHITE70, max_lines=3),
                        ],
                        spacing=3,
                        expand=True,
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            border_radius=15,
            padding=12,
        )
        exercise_list.controls.append(card)
    
    stretch_page = ft.Container(
        content=ft.Column(
            [
                ft.Container(height=30),
                ft.Text(
                    "STRETCH EXERCISES",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Gawin ang mga ito kapag pinaalalahanan ka!",
                    size=12,
                    color=ft.Colors.WHITE54,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=15),
                ft.Container(
                    content=exercise_list,
                    padding=ft.Padding(left=15, top=0, right=15, bottom=0),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        ),
    )
    
    # ================================================================
    # NAVIGATION (Ang Tabs sa ibaba)
    # ================================================================
    
    # Content area
    content_area = ft.Container(content=home_page, expand=True)
    
    def on_nav_change(e):
        if e.control.selected_index == 0:
            content_area.content = home_page
        else:
            content_area.content = stretch_page
        page.update()
    
    nav_bar = ft.NavigationBar(
        selected_index=0,
        on_change=on_nav_change,
        bgcolor=ft.Colors.GREY_900,
        indicator_color=ft.Colors.TEAL_700,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.MONITOR_HEART_OUTLINED,
                selected_icon=ft.Icons.MONITOR_HEART,
                label="Monitor",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SELF_IMPROVEMENT,
                selected_icon=ft.Icons.SELF_IMPROVEMENT,
                label="Exercises",
            ),
        ],
    )
    
    # Main Layout
    page.add(
        ft.Column(
            [content_area, nav_bar],
            expand=True,
            spacing=0,
        )
    )
    
    # ================================================================
    # DATABASE CHECKER (Background Thread)
    # ================================================================
    
    def check_database():
        nonlocal current_slouch_count, current_slouch_seconds
        
        while True:
            try:
                response = requests.get(FIREBASE_URL)
                data = response.json()
                
                if data and "status" in data:
                    status = data["status"]
                    
                    # I-update ang statistics kung meron
                    if "slouch_count" in data:
                        current_slouch_count = data["slouch_count"]
                        slouch_count_text.value = str(current_slouch_count)
                    if "total_slouch_seconds" in data:
                        current_slouch_seconds = data["total_slouch_seconds"]
                        slouch_time_text.value = str(int(current_slouch_seconds))
                    
                    if status == "GOOD":
                        status_container.bgcolor = ft.Colors.GREEN_800
                        status_icon.icon = ft.Icons.CHECK_CIRCLE
                        status_icon.color = ft.Colors.GREEN_200
                        status_text.value = "GOOD POSTURE"
                        sub_status.value = "Magaling! Ituloy mo 'yan!"
                        page.bgcolor = ft.Colors.GREY_900
                    elif status == "SLOUCHING":
                        status_container.bgcolor = ft.Colors.RED_800
                        status_icon.icon = ft.Icons.WARNING_ROUNDED
                        status_icon.color = ft.Colors.RED_200
                        status_text.value = "UMAYOS KA!"
                        sub_status.value = "Pumunta sa Exercises tab!"
                        page.bgcolor = ft.Colors.RED_900
                    
                    page.update()
                    
            except Exception as e:
                print(f"Database check error: {e}")
            
            time.sleep(1)
    
    threading.Thread(target=check_database, daemon=True).start()

ft.app(target=main)