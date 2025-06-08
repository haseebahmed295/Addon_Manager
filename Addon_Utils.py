import os
import platform
import pathlib
import re
import sys
from typing import List, Dict, Optional
from nicegui import ui

# --- Addon_Utils.py equivalent ---


class AddonInfo:
    """Represents metadata for a single Blender addon."""

    def __init__(self, bl_info: Dict, path: str, fallback_name: str):
        self.bl_info = bl_info
        self.path = path
        self.fallback_name = fallback_name

    def get_name(self) -> str:
        """Return the addon name, using fallback if 'name' is missing."""
        return self.bl_info.get("name", self.fallback_name)

    def __repr__(self):
        return f"AddonInfo(name={self.get_name()}, path={self.path})"


class BlenderVersion:
    """Represents a Blender version and its associated addons."""

    def __init__(self, version: str, path: pathlib.Path):
        self.version = version
        self.path = path
        self.addons: List[AddonInfo] = []

    def add_addon(self, addon: AddonInfo):
        self.addons.append(addon)

    def __repr__(self):
        return f"BlenderVersion(version={self.version}, addons_count={len(self.addons)})"


class BlenderAddonScanner:
    """Manages scanning and parsing of Blender addons across versions."""

    def __init__(self):
        self.base_paths = self._get_blender_addon_paths()
        self.versions: List[BlenderVersion] = []
        self.errors: List[str] = []

    def _get_blender_addon_paths(self) -> List[pathlib.Path]:
        """Return potential Blender addon directory paths based on the OS."""
        system = platform.system()
        user_home = pathlib.Path.home()
        addon_paths = []
        if system == "Windows":
            addon_paths.append(user_home / "AppData" /
                               "Roaming" / "Blender Foundation" / "Blender")
        elif system == "Darwin":  # macOS
            addon_paths.append(user_home / "Library" /
                               "Application Support" / "Blender")
        elif system == "Linux":
            addon_paths.append(user_home / ".config" / "blender")
        print(f"Detected OS: {system}, Base paths: {addon_paths}")  # Debug
        return addon_paths

    def _parse_bl_info(self, init_file: pathlib.Path) -> Optional[Dict]:
        """Parse the complete bl_info dictionary from an __init__.py file."""
        try:
            with open(init_file, "r", encoding="utf-8") as f:
                content = f.read()
                bl_info_match = re.search(
                    r'bl_info\s*=\s*{([^}]*)}', content, re.DOTALL)
                if not bl_info_match:
                    print(f"No bl_info found in {init_file}")  # Debug
                    return None
                # Debug
                print(
                    f"Found bl_info in {init_file}: {bl_info_match.group(1)}")
                bl_info_content = bl_info_match.group(1)
                bl_info = {}
                matches = re.finditer(
                    r'"([^"]+)"\s*:\s*("(.*?)"|\([^)]+\)|[^,\n]+)(?:,|$)', bl_info_content, re.DOTALL)
                for match in matches:
                    key = match.group(1)
                    value = match.group(2).strip()
                    if value.startswith('"') and value.endswith('"'):
                        bl_info[key] = value[1:-1]
                    elif value.startswith('(') and value.endswith(')'):
                        try:
                            tuple_values = eval(value) if value else ("N/A",)
                            bl_info[key] = ".".join(str(v)
                                                    for v in tuple_values)
                        except:
                            bl_info[key] = value
                    else:
                        bl_info[key] = value.strip()
                return bl_info
        except PermissionError as e:
            print(f"PermissionError in _parse_bl_info: {e}")  # Debug
            self.errors.append(f"Permission denied for {init_file}: {e}")
            return None
        except Exception as e:
            print(f"General error in _parse_bl_info: {e}")  # Debug
            self.errors.append(f"Error parsing {init_file}: {e}")
            return None

    def _get_addon_info(self, addon_path: pathlib.Path) -> AddonInfo:
        """Extract addon information from its __init__.py or zip file."""
        fallback_name = addon_path.stem if addon_path.suffix == ".zip" else addon_path.name
        print(f"Processing addon path: {addon_path}")  # Debug
        if addon_path.suffix == ".zip":
            return AddonInfo(
                bl_info={"name": fallback_name,
                         "version": "N/A (ZIP file)", "description": "Uninstalled addon (ZIP)"},
                path=str(addon_path),
                fallback_name=fallback_name
            )
        init_file = addon_path / "__init__.py"
        if not init_file.exists():
            print(f"No __init__.py found in {addon_path}")  # Debug
            return AddonInfo(
                bl_info={"name": fallback_name, "version": "N/A",
                         "description": "No __init__.py found"},
                path=str(addon_path),
                fallback_name=fallback_name
            )
        bl_info = self._parse_bl_info(init_file)
        if bl_info:
            return AddonInfo(bl_info=bl_info, path=str(addon_path), fallback_name=fallback_name)
        return AddonInfo(
            bl_info={"name": fallback_name, "version": "N/A",
                     "description": "Failed to parse bl_info"},
            path=str(addon_path),
            fallback_name=fallback_name
        )

    def scan(self) -> None:
        """Scan for Blender versions and their addons."""
        self.versions = []
        self.errors = []
        for base_path in self.base_paths:
            print(f"Scanning base path: {base_path}")  # Debug
            if not base_path.exists():
                print(f"Path does not exist: {base_path}")  # Debug
                continue
            for version_dir in base_path.iterdir():
                print(f"Found version dir: {version_dir}")  # Debug
                if version_dir.is_dir() and version_dir.name.replace(".", "").isdigit():
                    version = BlenderVersion(version_dir.name, version_dir)
                    addon_dir = version_dir / "scripts" / "addons"
                    print(f"Checking addon dir: {addon_dir}")  # Debug
                    if addon_dir.exists():
                        try:
                            for item in addon_dir.iterdir():
                                if item.is_dir() and item.name == "__pycache__":
                                    continue
                                if (item.is_dir() and (item / "__init__.py").exists()) or item.suffix == ".zip":
                                    try:
                                        addon_info = self._get_addon_info(item)
                                        version.add_addon(addon_info)
                                    except PermissionError as e:
                                        # Debug
                                        print(
                                            f"PermissionError for {item}: {e}")
                                        self.errors.append(
                                            f"Permission denied for {item}: {e}")
                                        continue
                                    except Exception as e:
                                        # Debug
                                        print(f"Error processing {item}: {e}")
                                        self.errors.append(
                                            f"Error processing {item}: {e}")
                                        continue
                        except PermissionError as e:
                            # Debug
                            print(f"PermissionError for {addon_dir}: {e}")
                            self.errors.append(
                                f"Permission denied for {addon_dir}: {e}")
                            continue
                    if version.addons:
                        self.versions.append(version)
        # Debug
        print(
            f"Scan complete. Versions: {self.versions}, Errors: {self.errors}")
