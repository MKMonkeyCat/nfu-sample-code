"""
此檔案為 ui 模組的工具函式檔，包含一些在 ui 模組中會用到的通用函式
"""


# https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797#cursor-controls
class ANSI:
    UP = "\033[A"  # 向上移動一行
    CLR_LINE = "\033[K"  # 清除從光標到行尾的內容
    HIDE_CURSOR = "\033[?25l"  # 隱藏光標
    SHOW_CURSOR = "\033[?25h"  # 顯示光標
    KEY_UP = "\x1b[A"  # 向上箭頭
    KEY_DOWN = "\x1b[B"  # 向下箭頭
    KEY_ENTER = ("\r", "\n")  # Enter
    KEY_SPACE = " "  # 空格
    KEY_CTRL_C = "\x03"  # Ctrl+C 中斷

    CLEAR_SCREEN = "\033[2J"  # 清除整個螢幕
    GO_HOME = "\033[H"  # 將光標移動到左上角


def clear_screen() -> None:
    """清除終端機畫面，將游標移動到左上角"""
    print(ANSI.CLEAR_SCREEN + ANSI.GO_HOME, end="")
