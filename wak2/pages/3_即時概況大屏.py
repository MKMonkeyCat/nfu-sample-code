from __future__ import annotations

from project.ui import configure_page, render_overview_app
from project.ui.texts import PAGE_TITLE_OVERVIEW


def main() -> None:
    configure_page(PAGE_TITLE_OVERVIEW)
    render_overview_app()


if __name__ == "__main__":
    main()
