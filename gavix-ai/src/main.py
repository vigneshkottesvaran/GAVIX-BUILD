"""Console entry point for GAVIX AI."""

from src.core.command_executor import execute_command


def handle_command(command: str) -> dict:
    """Execute one command and display its standardized user-facing result."""
    result = execute_command(command, input_fn=input, output_fn=print)
    if result["intent"] != "exit":
        print(f"GAVIX: {result['message']}")
    return result


def main() -> None:
    print("==============================")
    print("       GAVIX AI v0.10")
    print("==============================")
    print("Try: open chrome, open website https://example.com, open downloads,")
    print("     find files pdf, move file, delete file, delete folder, exit")

    while True:
        command = input("\nYou: ").strip()
        result = handle_command(command)
        if result["intent"] == "exit":
            print("GAVIX: Goodbye!")
            break


if __name__ == "__main__":
    main()
