from __future__ import annotations

from project.ui import configure_page, render_report_app


def main() -> None:
    configure_page("資料報告")
    render_report_app()


if __name__ == "__main__":
    main()
