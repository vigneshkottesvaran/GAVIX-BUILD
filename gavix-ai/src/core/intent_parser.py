"""Rule-based recognition for the English and tested Tanglish commands."""

import re


_FOLDERS = ("desktop", "documents", "downloads")
_EXIT_COMMANDS = {"exit", "quit", "stop", "goodbye", "veliya po", "niruthu", "pothum"}
_TRAILING_COMMAND = r"(?:open\s+pannu|open\s+pannunga|thira|thirakk)"


def normalize_command(command: str) -> str:
    """Lowercase and normalize spacing/punctuation for rule matching."""
    if not isinstance(command, str):
        return ""
    command = command.strip().lower()
    # Retain URL punctuation, while treating conversational punctuation as spaces.
    command = re.sub(r"[^\w\s./:-]", " ", command)
    return re.sub(r"\s+", " ", command).strip()


def _folder_target(text: str):
    """Return an approved folder name for a supported open-folder phrase."""
    names = "|".join(_FOLDERS)
    patterns = (
        rf"(?:open|show|go\s+to)\s+({names})(?:\s+folder)?",
        rf"({names})(?:\s+folder(?:-ah|\s+ah)?)?\s+{_TRAILING_COMMAND}",
        rf"({names})\s+thira",
    )
    for pattern in patterns:
        match = re.fullmatch(pattern, text)
        if match:
            return match.group(1)
    return None


def parse_intent(command: str) -> dict:
    """Identify a supported command, returning only the intent and optional target.

    Natural-language site names are preserved as labels; this parser never turns
    them into URLs. The browser skill accepts only explicit HTTP(S) URLs.
    """
    text = normalize_command(command)
    if not text:
        return {"intent": "unknown"}

    if text in _EXIT_COMMANDS:
        return {"intent": "exit"}

    # Match browser commands before generic site-name + open phrases.
    if re.fullmatch(
        r"(?:open|launch|start)\s+(?:chrome|browser)|"
        r"(?:chrome|browser)\s+(?:open|open\s+pannu|ah\s+open\s+pannu)",
        text,
    ):
        return {"intent": "open_chrome"}

    # Approved locations precede website rules so e.g. Downloads folder-ah
    # open pannu cannot be captured as a website target.
    folder = _folder_target(text)
    if folder:
        return {"intent": "open_folder", "target": folder}

    # Explicit URL commands and the tested website/site suffix form.
    explicit_site = re.fullmatch(
        r"(?:open\s+(?:website|site)|go\s+to\s+website|visit)(?:\s+(.+))?", text
    )
    if explicit_site:
        target = explicit_site.group(1)
        return {"intent": "open_website", **({"target": target.strip()} if target else {})}

    tanglish_site = re.fullmatch(
        rf"(.+?)\s+(?:website|site)\s+{_TRAILING_COMMAND}", text
    )
    if tanglish_site:
        return {"intent": "open_website", "target": tanglish_site.group(1).strip()}

    simple_site = re.fullmatch(rf"(.+?)\s+{_TRAILING_COMMAND}", text)
    if simple_site:
        target = simple_site.group(1).strip()
        if target not in {"chrome", "browser", *_FOLDERS}:
            return {"intent": "open_website", "target": target}

    # File searches. Strip only recognized trailing command words so keywords
    # remain useful while tested Tanglish command suffixes are not included.
    find_match = re.fullmatch(
        r"(?:find\s+files|search\s+files|find|search\s+for|look\s+for)(?:\s+(.+))?", text
    )
    if find_match:
        target = find_match.group(1)
        return {"intent": "find_files", **({"target": target.strip()} if target else {})}

    tanglish_find = re.fullmatch(
        r"(?:files?\s+)?(.+?)\s+(?:thedu|thedi|kandu\s+pidi|search\s+pannu)", text
    )
    if tanglish_find:
        return {"intent": "find_files", "target": tanglish_find.group(1).strip()}

    # Recognition only; command_router/main retain the explicit confirmation flow.
    if re.search(r"(?:delete|remove)\s+(?:the\s+)?(?:folder|directory)\b|"
                 r"\bfolder\s+(?:ah\s+)?(?:delete|remove)\s+pannu\b", text):
        return {"intent": "delete_folder"}
    if re.search(r"(?:delete|remove)\s+(?:the\s+)?file\b|"
                 r"\bfile\s+(?:ah\s+)?(?:delete|remove)\s+pannu\b|"
                 r"send\s+file\s+to\s+recycle\s+bin", text):
        return {"intent": "delete_file"}
    if re.search(r"\bmove\s+(?:this\s+)?(?:file|document)\b|"
                 r"\bfile\s+(?:ah\s+)?move\s+pannu\b", text):
        return {"intent": "move_file"}

    return {"intent": "unknown"}
