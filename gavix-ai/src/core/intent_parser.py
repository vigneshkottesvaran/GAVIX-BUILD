
import re


def normalize_command(command: str) -> str:
    """Normalize user input for simple command matching."""
    command = command.strip().lower()
    command = re.sub(r"[^\w\s./:-]", " ", command)
    command = re.sub(r"\s+", " ", command)
    return command


def parse_intent(command: str) -> dict:
    """Identify a supported intent without executing any action."""
    text = normalize_command(command)

    if not text:
        return {"intent": "unknown"}

    if text in {"exit", "quit", "stop", "goodbye"}:
        return {"intent": "exit"}

    # Open Chrome or the default browser.
    if any(phrase in text for phrase in (
        "open chrome",
        "chrome open",
        "launch chrome",
        "start chrome",
        "open browser",
        "browser open",
    )):
        return {"intent": "open_chrome"}

    # Open a website.
    website_match = re.search(
        r"(?:open website|open site|go to website|visit)\s+(.+)",
        text,
    )
    if website_match:
        return {
            "intent": "open_website",
            "target": website_match.group(1).strip(),
        }

    # Open an approved folder.
    folder_match = re.search(
        r"(?:open|show|go to)\s+(desktop|documents|downloads)\b",
        text,
    )
    if folder_match:
        return {
            "intent": "open_folder",
            "target": folder_match.group(1),
        }

    # Find files in Downloads.
    file_match = re.search(
        r"(?:find files|search files|find|search for|look for)"
        r"\s+(.+)",
        text,
    )
    if file_match:
        return {
            "intent": "find_files",
            "target": file_match.group(1).strip(),
        }

    # Sensitive actions are recognized, not executed here.
    if any(phrase in text for phrase in (
        "delete folder",
        "remove folder",
        "delete directory",
    )):
        return {"intent": "delete_folder"}

    if any(phrase in text for phrase in (
        "delete file",
        "remove file",
        "send file to recycle bin",
    )):
        return {"intent": "delete_file"}

    if any(phrase in text for phrase in (
        "move file",
        "move this file",
        "move document",
    )):
        return {"intent": "move_file"}

    return {"intent": "unknown"}
