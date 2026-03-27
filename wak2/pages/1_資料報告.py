from __future__ import annotations

from project.ui import configure_page, render_report_app
from project.ui.texts import PAGE_TITLE_REPORT


def main() -> None:
    configure_page(PAGE_TITLE_REPORT)
    render_report_app()


if __name__ == "__main__":
    main()
