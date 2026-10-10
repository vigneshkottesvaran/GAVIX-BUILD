
from src.skills.open_browser import open_chrome, open_website
from src.skills.open_folder import open_folder
from src.skills.find_files import find_files
from src.skills.move_file import move_file
from src.skills.delete_file import delete_file
from src.skills.delete_folder import delete_folder
from src.core.intent_parser import parse_intent



def handle_command(command: str) -> None:
    parsed = parse_intent(command)
    intent = parsed["intent"]

    if intent == "exit":
        return
    elif intent == "open_chrome":
        command = "open chrome"
    elif intent == "open_website":
        command = f"open website {parsed['target']}"
    elif intent == "open_folder":
        command = f"open {parsed['target']}"
    elif intent == "find_files":
        command = f"find files {parsed['target']}"
    elif intent == "move_file":
        command = "move file"
    elif intent == "delete_file":
        command = "delete file"
    elif intent == "delete_folder":
        command = "delete folder"
    else:
        print("GAVIX: Command not recognised yet.")
        return

    command = command.strip()
    normalized = command.lower()


    if normalized in {"exit", "quit"}:
        return

    if normalized in {"open chrome", "chrome open pannu", "open browser"}:
        success = open_chrome()
        print(
            "GAVIX: Chrome launch requested."
            if success
            else "GAVIX: Could not launch Chrome."
        )

    elif normalized.startswith("open website "):
        url = command[len("open website "):].strip()
        try:
            success = open_website(url)
            print(
                "GAVIX: Website opening requested."
                if success
                else "GAVIX: Browser could not open the website."
            )
        except ValueError as error:
            print(f"GAVIX: {error}")

    elif normalized in {
        "open desktop", "open documents", "open downloads"
    }:
        folder_name = normalized.removeprefix("open ")
        success = open_folder(folder_name)
        if success:
            print(f"GAVIX: Opened {folder_name}.")
        else:
            print(f"GAVIX: Could not open {folder_name}.")

    elif normalized.startswith("find files "):
        keyword = command[len("find files "):].strip()

        try:
            results = find_files(keyword, "downloads")

            if results:
                print(f"GAVIX: Found {len(results)} matching file(s):")
                for path in results:
                    print(f"  {path}")
            else:
                print("GAVIX: No matching files found.")

        except (ValueError, FileNotFoundError, PermissionError) as error:
            print(f"GAVIX: Search failed: {error}")
    
    
    elif normalized == "delete file":
        keyword = input(
            "GAVIX: Enter filename or keyword: "
        ).strip()

        try:
            results = find_files(keyword, "downloads")

            if not results:
                print("GAVIX: No matching files found.")
            else:
                print("\nGAVIX: Matching files:")
                for index, path in enumerate(results, start=1):
                    print(f"  {index}. {path}")

                choice = input(
                    "\nGAVIX: Enter the file number "
                    "to delete (or 'cancel'): "
                ).strip()

                if choice.lower() == "cancel":
                    print("GAVIX: Delete cancelled.")
                elif not choice.isdigit():
                    print("GAVIX: Invalid selection. Nothing was deleted.")
                elif not 1 <= int(choice) <= len(results):
                    print("GAVIX: Invalid file number. Nothing was deleted.")
                else:
                    source = results[int(choice) - 1]

                    print(f"\nGAVIX: Selected file: {source}")
                    confirmation = input(
                        "GAVIX: Type 'CONFIRM' to send "
                        "this file to the Recycle Bin: "
                    ).strip()

                    if confirmation == "CONFIRM":
                        delete_file(str(source), confirmed=True)
                    else:
                        print("GAVIX: Delete cancelled. Nothing was deleted.")

        except (ValueError, FileNotFoundError, PermissionError) as error:
            print(f"GAVIX: Delete failed: {error}")
    
    elif normalized == "delete folder":
        keyword = input(
            "GAVIX: Enter folder name or keyword: "
        ).strip()

        if not keyword:
            print("GAVIX: Folder name cannot be empty.")
        else:
            try:
                from pathlib import Path

                allowed = [
                    Path.home() / "Desktop",
                    Path.home() / "Documents",
                    Path.home() / "Downloads",
                ]

                results = sorted(
                    path
                    for base in allowed
                    if base.is_dir()
                    for path in base.iterdir()
                    if path.is_dir()
                    and keyword.lower() in path.name.lower()
                )

                if not results:
                    print("GAVIX: No matching folders found.")
                else:
                    print("\nGAVIX: Matching folders:")
                    for index, path in enumerate(results, start=1):
                        print(f"  {index}. {path}")

                    choice = input(
                        "\nGAVIX: Enter folder number "
                        "(or 'cancel'): "
                    ).strip()

                    if choice.lower() == "cancel":
                        print("GAVIX: Folder deletion cancelled.")
                    elif not choice.isdigit():
                        print("GAVIX: Invalid selection. Nothing was deleted.")
                    elif not 1 <= int(choice) <= len(results):
                        print("GAVIX: Invalid folder number. Nothing was deleted.")
                    else:
                        source = results[int(choice) - 1]
                        print(f"\nGAVIX: Selected folder: {source}")
                        print(
                            "GAVIX: Its contents will also go to "
                            "the Recycle Bin."
                        )

                        confirmation = input(
                            "GAVIX: Type 'CONFIRM' to continue: "
                        ).strip()

                        if confirmation == "CONFIRM":
                            delete_folder(str(source), confirmed=True)
                        else:
                            print(
                                "GAVIX: Folder deletion cancelled. "
                                "Nothing was deleted."
                            )

            except (OSError, ValueError) as error:
                print(f"GAVIX: Folder search failed: {error}")

    elif normalized == "move file":
        keyword = input("GAVIX: Enter filename or keyword: ").strip()

        try:
            results = find_files(keyword, "downloads")

            if not results:
                print("GAVIX: No matching files found.")
            else:
                print("\nGAVIX: Matching files:")
                for index, path in enumerate(results, start=1):
                    print(f"  {index}. {path}")

                choice = input(
                    "\nGAVIX: Enter the file number to move "
                    "(or 'cancel'): "
                ).strip()

                if choice.lower() == "cancel":
                    print("GAVIX: Move cancelled.")
                elif not choice.isdigit():
                    print("GAVIX: Invalid selection. Nothing was moved.")
                elif not 1 <= int(choice) <= len(results):
                    print("GAVIX: Invalid file number. Nothing was moved.")
                else:
                    source = results[int(choice) - 1]

                    print(f"\nGAVIX: Source: {source}")
                    print("GAVIX: Destination folder: Documents")

                    confirmation = input(
                        "GAVIX: Type 'CONFIRM' to move this file: "
                    ).strip()

                    if confirmation == "CONFIRM":
                        move_file(
                            str(source),
                            "documents",
                            confirmed=True,
                        )
                    else:
                        print("GAVIX: Move cancelled. No file was moved.")

        except (ValueError, FileNotFoundError, PermissionError) as error:
            print(f"GAVIX: File operation failed: {error}")


    else:
        print("GAVIX: Command not recognised yet.")


def main() -> None:
    print("==============================")
    print("       GAVIX AI v0.2")
    print("==============================")
    print("Commands:")
    print("  open chrome")
    print("  open website https://example.com")
    print("  open desktop")
    print("  open documents")
    print("  open downloads")
    print("  find files pdf")
    print("  move file")
    print("  delete file")
    print("  delete folder")
    print("  exit")
    while True:
        command = input("\nYou: ").strip()

        if command.lower() in {"exit", "quit"}:
            print("GAVIX: Goodbye!")
            break

        handle_command(command)


if __name__ == "__main__":
    main()
