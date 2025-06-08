import os
import platform
import pathlib
import re
import sys
from typing import List, Dict, Optional
from nicegui import ui

from Addon_Utils import BlenderAddonScanner


def create_ui():
    """Create the NiceGUI interface for displaying Blender addons."""
    scanner = BlenderAddonScanner()
    scanner.scan()
    print("NiceGUI app initialized")  # Debug

    # Add CSS for styling
    ui.add_head_html("""
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
            .header { font-size: 24px; color: #4CAF50; text-align: center; margin-bottom: 20px; }
            .addon-card { margin-bottom: 10px;
                width: 100%;
            }
            .addon-title { font-weight: bold; }
            .addon-details { padding: 10px; background-color: #fff; border: 1px solid #ddd; }
            .error-log { margin-top: 20px; padding: 10px; background-color: #f8d7da; border: 1px solid #dc3545; }
            .footer { margin-top: 20px; text-align: center; color: #666; }
        </style>
    """)

    # Header
    ui.label("Blender Addon Manager").classes("header")
    print("Header added")  # Debug

    # Addon list with toggleable details
    with ui.card().classes("addon-card"):
        ui.label("Addon List").style("font-size: 18px; font-weight: bold;")
        if not scanner.versions:
            ui.label("No addons found.").style("color: #dc3545")
            print("No addons found, displaying fallback message")  # Debug
        else:
            for version in scanner.versions:
                for addon in version.addons:
                    with ui.expansion(f"{addon.get_name()} (Blender {version.version})").classes("addon-card"):
                        ui.label(
                            f"Author: {addon.bl_info.get('author', 'N/A')}").classes("addon-title")
                        with ui.card().classes("addon-details"):
                            ui.label(f"Path: {addon.path}")
                            for key, value in addon.bl_info.items():
                                if key not in ["name", "author"]:
                                    ui.label(f"{key.capitalize()}: {value}")
                    # Debug
                    print(f"Added expansion for addon: {addon.get_name()}")

    # Error log
    with ui.card().classes("error-log"):
        ui.label("Error Log").style("font-size: 18px; font-weight: bold;")
        if scanner.errors:
            for error in scanner.errors:
                ui.label(error).style("color: #dc3545")
        else:
            ui.label("No errors encountered during scan.").style(
                "color: #28a745")
    print("Error log added")  # Debug

    # Footer
    ui.label("Blender Addon Manager - Powered by NiceGUI").classes("footer")
    print("UI fully rendered")  # Debug
    ui.run(title="Blender Addon Manager", port=8080, reload=False ,native=True)


create_ui()
