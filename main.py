import os
import platform
import pathlib
import re
import sys
from typing import List, Dict, Optional
from nicegui import ui

from Addon_Utils import BlenderAddonScanner
from utils import open_in_code_thread

search_query = ''


def update_search(query):
    global search_query
    search_query = query
    display_addons.refresh()


def create_ui():
    """Create the NiceGUI interface for displaying Blender addons with search and actions."""
    scanner = BlenderAddonScanner()
    scanner.scan()
    all_addons = [(version.version, addon)
                  for version in scanner.versions for addon in version.addons]

    # Add CSS for styling
    ui.add_head_html("""
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
            .header { font-size: 24px; color: #4CAF50; text-align: center; margin-bottom: 20px; }
            .addon-card { margin-bottom: 10px; width: 100%; }
            .addon-title { font-weight: bold; }
            .addon-details { padding: 10px; background-color: #fff; border: 1px solid #ddd; }
            .error-log { margin-top: 20px; padding: 10px; background-color: #f8d7da; border: 1px solid #dc3545; }
            .footer { margin-top: 20px; text-align: center; color: #666; }
        </style>
    """)

    # Header
    ui.label("Blender Addon Manager").classes("header")

    # Search input
    ui.input(label="Search Addons", placeholder="Type to search...",
             on_change=lambda e: update_search(e.value))

    # Addon list with toggleable details and actions
    @ui.refreshable
    def display_addons():
        filtered_addons = [
            (ver, addon) for ver, addon in all_addons
            if search_query.lower() in addon.get_name().lower()
            or search_query.lower() in addon.bl_info.get('description', '').lower()
            or search_query.lower() in addon.bl_info.get('author', '').lower()
        ]
        with ui.card().classes("addon-card"):
            ui.label("Addon List").style("font-size: 18px; font-weight: bold;")
            if not filtered_addons:
                ui.label("No addons found.").style("color: #dc3545")
            else:
                for ver, addon in filtered_addons:
                    with ui.expansion(f"{addon.get_name()} (Blender {ver})").classes("addon-card"):
                        with ui.row():
                            search_input = ui.input(label="Search Addons", placeholder="Type to search...",
                                                    on_change=lambda e: update_search(e.value))
                            ui.button('Clear', on_click=lambda: (
                                search_input.set_value(''), update_search('')))
                            with ui.dropdown_button('Actions', auto_close=True):
                                ui.menu_item(
                                    'Open in Code', lambda path=addon.path: open_in_code_thread(path))
                        with ui.card().classes("addon-details"):
                            ui.label(f"Path: {addon.path}")
                            for key, value in addon.bl_info.items():
                                if key not in ["name", "author"]:
                                    ui.label(f"{key.capitalize()}: {value}")

    display_addons()

    # Error log
    with ui.card().classes("error-log"):
        ui.label("Error Log").style("font-size: 18px; font-weight: bold;")
        if scanner.errors:
            for error in scanner.errors:
                ui.label(error).style("color: #dc3545")
        else:
            ui.label("No errors encountered during scan.").style(
                "color: #28a745")

    # Footer
    ui.label("Blender Addon Manager - Powered by NiceGUI").classes("footer")
    ui.run(title="Blender Addon Manager", port=8080, reload=False, native=True)


create_ui()
