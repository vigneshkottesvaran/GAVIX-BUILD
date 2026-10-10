
from pathlib import Path
from send2trash import send2trash


ALLOWED_FOLDERS = {
    "desktop": Path.home() / "Desktop",
    "documents": Path.home() / "Documents",
    "downloads": Path.home() / "Downloads",
}


def delete_file(source: str, confirmed: bool = False) -> bool:
    """Move an approved file to the Windows Recycle Bin."""

    try:
        source_path = Path(source).expanduser().resolve(strict=True)

        if not source_path.is_file():
            print("GAVIX: Source must be a file.")
            return False

        approved_source = any(
            source_path.parent == folder.resolve()
            for folder in ALLOWED_FOLDERS.values()
            if folder.is_dir()
        )

        if not approved_source:
            print("GAVIX: File is outside approved folders.")
            return False

        if confirmed is not True:
            print(f"GAVIX: File selected: {source_path}")
            print("GAVIX: Explicit confirmation is required.")
            return False

        send2trash(str(source_path))
        print(f"GAVIX: File sent to Recycle Bin: {source_path.name}")
        return True

    except FileNotFoundError:
        print("GAVIX: File not found.")
        return False
    except PermissionError:
        print("GAVIX: Permission denied.")
        return False
    except OSError as error:
        print(f"GAVIX: Could not send file to Recycle Bin: {error}")
        return False
