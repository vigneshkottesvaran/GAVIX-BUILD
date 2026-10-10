
import subprocess
import webbrowser


def open_website(url: str = "https://www.google.com") -> bool:
    """Open a website in the default browser."""
    if not url.startswith(("https://", "http://")):
        raise ValueError("Only HTTP and HTTPS URLs are allowed.")

    return webbrowser.open(url)


def open_chrome() -> bool:
    """Open Chrome using the Windows application launcher."""
    try:
        subprocess.Popen(["cmd", "/c", "start", "", "chrome"])
        return True
    except OSError:
        return False


if __name__ == "__main__":
    success = open_chrome()
    print("GAVIX: Chrome launch requested." if success else
          "GAVIX: Could not launch Chrome.")
