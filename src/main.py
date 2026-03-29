"""
SystemMonitor - Entry Point
Minimal main module that launches the application.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import SystemMonitorApp


def main():
    """Launch the SystemMonitor application."""
    app = SystemMonitorApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()


if __name__ == "__main__":
    main()
