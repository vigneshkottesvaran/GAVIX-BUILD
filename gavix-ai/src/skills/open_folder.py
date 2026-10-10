
import os
from pathlib import Path


ALLOWED_FOLDERS = {
    "desktop": Path.home() / "Desktop",
    "documents": Path.home() / "Documents",
    "downloads": Path.home() / "Downloads",
}


def open_folder(folder_name: str) -> bool:
    """Open a known folder in Windows File Explorer."""
    name = folder_name.strip().lower()
    folder_path = ALLOWED_FOLDERS.get(name)

    if folder_path is None:
        print(f"GAVIX: Unknown folder: {folder_name}")
        print("Available folders: Desktop, Documents, Downloads")
        return False

    if not folder_path.is_dir():
        print(f"GAVIX: Folder not found: {folder_path}")
        return False

    try:
        os.startfile(str(folder_path))
        return True
    except OSError as error:
        print(f"GAVIX: Could not open folder: {error}")
        return False
