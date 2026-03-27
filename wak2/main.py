from __future__ import annotations

from project.ui import configure_page, render_vote_app


def main() -> None:
    configure_page("投票系統")
    render_vote_app()


if __name__ == "__main__":
    main()
