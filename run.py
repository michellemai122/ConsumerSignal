#!/usr/bin/env python3
"""
One-command launcher for the Startup Intelligence dashboard.

Why this exists:
  - macOS grabs port 5000 for AirPlay Receiver, which silently collides with
    Flask's default. This finds a free port instead.
  - Opening index.html directly (file://) breaks the app because the frontend
    fetches from /api/*. You MUST run through this server. This does that and
    opens the browser to the right URL for you.

Usage:
    python3 run.py
"""
import socket
import threading
import webbrowser

from app.api import app


def find_free_port(preferred=5000):
    """Return `preferred` if it's free, otherwise an OS-assigned open port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            pass
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main():
    port = find_free_port(5000)
    url = f"http://127.0.0.1:{port}/"
    print(f"\n  Startup Intelligence dashboard running at: {url}")
    print("  Press CTRL+C to stop.\n")
    # Open the browser shortly after the server starts.
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
