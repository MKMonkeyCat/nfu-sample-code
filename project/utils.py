from typing import Any, Optional


# https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797#color-codes
class Style:
    """ANSI 顏色碼與字體樣式碼"""

    BLACK = "\033[30m"  # 黑色
    RED = "\033[31m"  # 紅色
    GREEN = "\033[32m"  # 綠色
    YELLOW = "\033[33m"  # 黃色
    BLUE = "\033[34m"  # 藍色
    PURPLE = "\033[35m"  # 紫色
    CYAN = "\033[36m"  # 青色
    WHITE = "\033[37m"  # 白色

    GRAY = "\033[90m"  # 灰色
    RESET = "\033[0m"  # 重置樣式
    BOLD = "\033[1m"  # 粗體

    @staticmethod
    def paint(text: Any, style_code: str) -> str:
        """將指定的樣式套用到文字上，並在結尾重置樣式，確保不影響後續輸出"""
        return f"{style_code}{text}{Style.RESET}"


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
