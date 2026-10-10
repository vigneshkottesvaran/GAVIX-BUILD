"""Route commands to skills and return a consistent execution result."""

from contextlib import redirect_stdout
from importlib import import_module
from io import StringIO
from pathlib import Path
from typing import Callable, Optional

from src.core.command_router import route_command
from src.skills import find_files as find_files_module
from src.skills.open_browser import open_chrome, open_website
from src.skills.open_folder import open_folder


InputFunction = Callable[[str], str]
OutputFunction = Callable[[str], None]


def _result(
    success: bool,
    intent: str,
    message: str,
    data=None,
    needs_clarification: bool = False,
) -> dict:
    return {
        "success": success,
        "intent": intent,
        "message": message,
        "data": data,
        "needs_clarification": needs_clarification,
    }


def execute_command(
    command: str,
    *,
    input_fn: Optional[InputFunction] = None,
    output_fn: Optional[OutputFunction] = None,
) -> dict:
    """Execute a routed command; destructive actions require interactive confirmation.

    Without an input function, move/delete intents stop with a clarification result.
    The interactive paths still call the existing skills with ``confirmed=True``
    only after the user types the exact word ``CONFIRM``.
    """
    route = route_command(command)
    intent = route["intent"]
    skill = route["skill"]
    target = route["target"]
    ask = input_fn
    say = output_fn or (lambda message: None)

    if intent == "unknown" or skill is None:
        return _result(False, intent, "Command not recognised yet.")
    if intent == "exit":
        return _result(True, intent, "Goodbye.")
    if intent == "open_website" and not target:
        return _result(False, intent, "Which website should I open?", needs_clarification=True)
    if intent == "find_files" and not target:
        return _result(False, intent, "Which files should I search for?", needs_clarification=True)
    if intent in {"move_file", "delete_file", "delete_folder"} and ask is None:
        subject = "file" if intent != "delete_folder" else "folder"
        return _result(
            False, intent, f"Which {subject} should I {intent.replace('_', ' ')}?",
            needs_clarification=True,
        )

    try:
        # Silence legacy skill status prints so callers receive one standardized
        # user-facing message from this execution layer.
        if intent == "open_chrome":
            success = bool(_invoke_skill_silently(open_chrome))
            message = "Chrome launch requested." if success else "Could not launch Chrome."
            return _result(success, intent, message)

        if intent == "open_website":
            success = bool(_invoke_skill_silently(open_website, target))
            message = "Website opening requested." if success else "Browser could not open the website."
            return _result(success, intent, message, {"target": target})

        if intent == "open_folder":
            success = bool(_invoke_skill_silently(open_folder, target))
            message = f"Opened {target}." if success else f"Could not open {target}."
            return _result(success, intent, message, {"target": target})

        if intent == "find_files":
            files = find_files_module.find_files(target, "downloads")
            paths = [str(path) for path in files]
            message = f"Found {len(paths)} matching file(s)." if paths else "No matching files found."
            return _result(bool(paths), intent, message, {"files": paths})

        if intent in {"move_file", "delete_file"}:
            return _execute_file_action(intent, ask, say)

        if intent == "delete_folder":
            return _execute_folder_delete(ask, say)

        return _result(False, intent, "Command not recognised yet.")
    except Exception as error:
        return _result(False, intent, _safe_error_message(error))


def _safe_error_message(error: Exception) -> str:
    if isinstance(error, ValueError):
        return str(error)
    if isinstance(error, FileNotFoundError):
        return "The requested file or folder was not found."
    if isinstance(error, PermissionError):
        return "Permission was denied while completing the request."
    return "The request could not be completed."


def _run_move_file(*args, **kwargs):
    return import_module("src.skills.move_file").move_file(*args, **kwargs)


def _run_delete_file(*args, **kwargs):
    return import_module("src.skills.delete_file").delete_file(*args, **kwargs)


def _run_delete_folder(*args, **kwargs):
    return import_module("src.skills.delete_folder").delete_folder(*args, **kwargs)


def _invoke_skill_silently(function, *args, **kwargs):
    with redirect_stdout(StringIO()):
        return function(*args, **kwargs)


def _ask_for_target(ask: InputFunction, label: str) -> Optional[str]:
    target = ask(f"Enter {label} (or 'cancel'): ").strip()
    return target if target and target.lower() != "cancel" else None


def _choose_path(paths, ask: InputFunction, say: OutputFunction, label: str):
    if not paths:
        return None
    for index, path in enumerate(paths, start=1):
        say(f"  {index}. {path}")
    choice = ask(f"Enter the {label} number (or 'cancel'): ").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(paths):
        return None
    return paths[int(choice) - 1]


def _execute_file_action(intent: str, ask: InputFunction, say: OutputFunction) -> dict:
    operation = "move" if intent == "move_file" else "delete"
    keyword = _ask_for_target(ask, "filename or keyword")
    if keyword is None:
        return _result(False, intent, f"{operation.capitalize()} cancelled; no file was changed.")

    files = find_files_module.find_files(keyword, "downloads")
    if not files:
        return _result(False, intent, "No matching files found.", {"files": []})

    selected = _choose_path(files, ask, say, "file")
    if selected is None:
        return _result(False, intent, f"{operation.capitalize()} cancelled; no file was changed.")

    destination = "documents" if intent == "move_file" else None
    if destination:
        say(f"Destination folder: {destination.title()}")
    confirmation = ask("Type 'CONFIRM' to continue: ").strip()
    if confirmation != "CONFIRM":
        return _result(False, intent, f"{operation.capitalize()} cancelled; no file was changed.")

    if intent == "move_file":
        success = bool(_invoke_skill_silently(
            _run_move_file, str(selected), destination, confirmed=True
        ))
        message = "File moved to Documents." if success else "File could not be moved."
    else:
        success = bool(_invoke_skill_silently(_run_delete_file, str(selected), confirmed=True))
        message = "File sent to the Recycle Bin." if success else "File could not be deleted."
    return _result(success, intent, message, {"path": str(selected)})


def _execute_folder_delete(ask: InputFunction, say: OutputFunction) -> dict:
    keyword = _ask_for_target(ask, "folder name or keyword")
    if keyword is None:
        return _result(False, "delete_folder", "Folder deletion cancelled; nothing was changed.")

    approved = [Path.home() / name for name in ("Desktop", "Documents", "Downloads")]
    folders = sorted(
        path for base in approved if base.is_dir() for path in base.iterdir()
        if path.is_dir() and keyword.casefold() in path.name.casefold()
    )
    if not folders:
        return _result(False, "delete_folder", "No matching folders found.", {"folders": []})

    selected = _choose_path(folders, ask, say, "folder")
    if selected is None:
        return _result(False, "delete_folder", "Folder deletion cancelled; nothing was changed.")

    say("The selected folder and its contents will go to the Recycle Bin.")
    confirmation = ask("Type 'CONFIRM' to continue: ").strip()
    if confirmation != "CONFIRM":
        return _result(False, "delete_folder", "Folder deletion cancelled; nothing was changed.")

    success = bool(_invoke_skill_silently(_run_delete_folder, str(selected), confirmed=True))
    message = "Folder sent to the Recycle Bin." if success else "Folder could not be deleted."
    return _result(success, "delete_folder", message, {"path": str(selected)})
