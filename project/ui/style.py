"""
此檔案為 ui 模組的樣式定義檔，包含 ANSI 顏色碼與字體樣式碼，以及一個方便的 paint 函式用於套用樣式
"""


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
    def paint(text: str, style_code: str) -> str:
        return f"{style_code}{text}{Style.RESET}"
