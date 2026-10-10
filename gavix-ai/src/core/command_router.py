
from src.core.intent_parser import parse_intent


def route_command(command: str) -> dict:
    """Parse a command and return its routing decision."""
    parsed = parse_intent(command)
    intent = parsed.get("intent", "unknown")

    routes = {
        "open_chrome": "open_browser",
        "open_website": "open_browser",
        "open_folder": "open_folder",
        "find_files": "find_files",
        "move_file": "move_file",
        "delete_file": "delete_file",
        "delete_folder": "delete_folder",
        "exit": "exit",
    }

    return {
        "intent": intent,
        "skill": routes.get(intent),
        "target": parsed.get("target"),
    }
