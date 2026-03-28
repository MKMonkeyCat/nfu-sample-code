from __future__ import annotations

import sys

if __name__ == "__main__":
    if sys.argv[1].endswith("--cli"):
        from project.__main__ import main

        main()
    else:
        from project.web import run_web

        run_web()
