from typing import Optional

from project.ui.style import Style


def fmt_score(v: Optional[float], color: str = "") -> str:
    """
    將分數格式化為帶有顏色的字串，如果分數為 None 則顯示灰色的 ---.-
    如果提供了 color 參數則使用該顏色，否則根據分數的範圍自動決定顏色 (60 以下為紅色，80-89 為黃色，90 以上為綠色)
    """
    if v is None:
        return Style.paint("---.-", Style.GRAY)

    display_color = color
    if not color:
        if v >= 90:
            display_color = Style.GREEN
        elif v >= 80:
            display_color = Style.YELLOW
        elif v < 60:
            display_color = Style.RED

    text = f"{v:5.1f}"
    return Style.paint(text, display_color) if display_color else text
