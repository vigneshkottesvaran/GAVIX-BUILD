import subprocess
import webbrowser
from urllib.parse import urlsplit

def open_website(url: str = "https://www.google.com") -> bool:
    """Open a valid HTTP or HTTPS URL."""
    if not isinstance(url, str) or not url.strip():
        raise ValueError("A valid HTTP or HTTPS URL is required.")

    url = url.strip()

    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname
    except ValueError as error:
        raise ValueError("Invalid URL.") from error

    if parsed.scheme.lower() not in {"http", "https"} or not hostname:
        raise ValueError("Only valid HTTP and HTTPS URLs are allowed.")

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
