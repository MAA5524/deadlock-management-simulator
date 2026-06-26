#!/usr/bin/env python3
"""
Deadlock Handler — سیستم مقابله با بن‌بست
Operating Systems Course Project

Entry point for the application.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import DeadlockApp


def main():
    app = DeadlockApp()
    app.mainloop()


if __name__ == "__main__":
    main()
