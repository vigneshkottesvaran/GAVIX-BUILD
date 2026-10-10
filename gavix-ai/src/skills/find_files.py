
from pathlib import Path


SEARCH_LOCATIONS = {
    "desktop": Path.home() / "Desktop",
    "documents": Path.home() / "Documents",
    "downloads": Path.home() / "Downloads",
}


def find_files(
    keyword: str,
    location: str = "desktop",
    limit: int = 20,
) -> list[Path]:
    """Find files by filename without changing them."""
    folder = SEARCH_LOCATIONS.get(location.strip().lower())

    if folder is None:
        raise ValueError(
            "Choose desktop, documents, or downloads."
        )

    if not folder.is_dir():
        raise FileNotFoundError(
            f"Folder does not exist: {folder}"
        )

    keyword = keyword.strip().lower()

    if not keyword:
        raise ValueError("Search keyword cannot be empty.")

    if limit < 1 or limit > 100:
        raise ValueError("Limit must be between 1 and 100.")

    results = []

    for path in folder.rglob("*"):
        if path.is_file() and keyword in path.name.lower():
            results.append(path)

            if len(results) >= limit:
                break

    return results


if __name__ == "__main__":
    try:
        matches = find_files("pdf", "downloads")

        if matches:
            for path in matches:
                print(path)
        else:
            print("GAVIX: No matching files found.")

    except (ValueError, FileNotFoundError, PermissionError) as error:
        print(f"GAVIX: {error}")
