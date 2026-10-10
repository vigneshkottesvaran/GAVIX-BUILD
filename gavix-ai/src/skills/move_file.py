
from pathlib import Path
import shutil


ALLOWED_FOLDERS = {
    "desktop": Path.home() / "Desktop",
    "documents": Path.home() / "Documents",
    "downloads": Path.home() / "Downloads",
}


def move_file(
    source: str,
    destination_folder: str,
    confirmed: bool = False,
) -> bool:
    """Move a file between approved folders after explicit confirmation."""

    try:
        source_path = Path(source).expanduser().resolve(strict=True)
        folder = ALLOWED_FOLDERS.get(destination_folder.strip().lower())

        if folder is None:
            print(
                "GAVIX: Destination must be desktop, "
                "documents, or downloads."
            )
            return False

        if not source_path.is_file():
            print("GAVIX: Source must be a file.")
            return False

        # Only allow files directly inside approved folders.
        approved_source = any(
            source_path.parent == allowed.resolve()
            for allowed in ALLOWED_FOLDERS.values()
            if allowed.is_dir()
        )

        if not approved_source:
            print("GAVIX: Source is outside approved folders.")
            return False

        if not folder.is_dir():
            print("GAVIX: Destination folder not found.")
            return False

        folder = folder.resolve()
        destination = folder / source_path.name

        if source_path == destination:
            print("GAVIX: Source and destination are the same.")
            return False

        if destination.exists():
            print("GAVIX: A file with that name already exists.")
            print("GAVIX: Nothing was moved.")
            return False

        if confirmed is not True:
            print(f"GAVIX: Source: {source_path}")
            print(f"GAVIX: Destination: {destination}")
            print("GAVIX: Explicit confirmation is required.")
            return False

        shutil.move(str(source_path), str(destination))
        print(f"GAVIX: File moved to {destination}")
        return True

    except FileNotFoundError:
        print("GAVIX: Source file or folder not found.")
        return False
    except PermissionError:
        print("GAVIX: Permission denied. Nothing was moved.")
        return False
    except OSError as error:
        print(f"GAVIX: Move failed: {error}")
        return False
