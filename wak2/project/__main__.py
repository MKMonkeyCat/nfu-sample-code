from __future__ import annotations

from project.ui import configure_page, render_vote_app
from project.ui.texts import PAGE_TITLE_VOTE


def main() -> None:
    configure_page(PAGE_TITLE_VOTE)
    render_vote_app()


if __name__ == "__main__":
    main()
