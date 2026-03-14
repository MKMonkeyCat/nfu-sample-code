from typing import Final


class Style:
    BLUE: Final[str] = "\033[34m"
    CYAN: Final[str] = "\033[36m"
    GREEN: Final[str] = "\033[32m"
    GRAY: Final[str] = "\033[90m"
    YELLOW: Final[str] = "\033[33m"
    RED: Final[str] = "\033[31m"
    RESET: Final[str] = "\033[0m"
    BOLD: Final[str] = "\033[1m"

    @staticmethod
    def paint(text: str, style_code: str) -> str:
        return f"{style_code}{text}{Style.RESET}"
