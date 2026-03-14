from typing import Optional

from project.ui.style import Style


def fmt_score(v: Optional[float], color: str = "") -> str:
    if v is None:
        return Style.paint("---.-", Style.GRAY)

    display_color = color
    if not color:
        if v < 60:
            display_color = Style.RED
        elif v >= 90:
            display_color = Style.GREEN
        elif v >= 80:
            display_color = Style.YELLOW

    text = f"{v:5.1f}"
    return Style.paint(text, display_color) if display_color else text
