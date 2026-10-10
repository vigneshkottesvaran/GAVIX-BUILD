
from pathlib import Path
from send2trash import send2trash


ALLOWED_FOLDERS = {
    "desktop": Path.home() / "Desktop",
    "documents": Path.home() / "Documents",
    "downloads": Path.home() / "Downloads",
}


def delete_folder(source: str, confirmed: bool = False) -> bool:
    """Move an approved folder to the Windows Recycle Bin."""

    try:
        source_path = Path(source).expanduser().resolve(strict=True)

        if not source_path.is_dir():
            print("GAVIX: Source must be a folder.")
            return False

        approved_parent = any(
            source_path.parent == folder.resolve()
            for folder in ALLOWED_FOLDERS.values()
            if folder.is_dir()
        )

        if not approved_parent:
            print("GAVIX: Folder must be directly inside Desktop, Documents, or Downloads.")
            return False

        if not confirmed:
            print(f"GAVIX: Folder selected: {source_path}")
            print("GAVIX: Explicit confirmation is required.")
            return False

        send2trash(str(source_path))
        print(f"GAVIX: Folder sent to Recycle Bin: {source_path.name}")
        return True

    except FileNotFoundError:
        print("GAVIX: Folder not found.")
        return False
    except PermissionError:
        print("GAVIX: Permission denied.")
        return False
    except OSError as error:
        print(f"GAVIX: Could not send folder to Recycle Bin: {error}")
        return False
