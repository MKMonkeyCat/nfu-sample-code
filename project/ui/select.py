import sys
import termios
import tty
from typing import Generic, List, Sequence, TypeVar

from .style import Style

_T = TypeVar("_T")

# ANSI 控制碼
_UP = "\033[A"  # 向上移動一行
_CLR = "\033[K"  # 清除行尾
_HIDE = "\033[?25l"  # 隱藏游標
_SHOW = "\033[?25h"  # 顯示游標


class InteractiveSelector(Generic[_T]):
    def __init__(self, question: str, options: Sequence[_T]):
        self.question: str = question
        self.options: Sequence[_T] = options
        self.selected: List[bool] = [False] * len(options)
        self.current_index: int = 0

    def _get_key(self) -> str:
        fd = sys.stdin.fileno()  # 讀取單個按鍵（包含方向鍵的轉義序列）
        old_settings = termios.tcgetattr(fd)  # 保存當前終端設置
        try:
            tty.setraw(fd)  # 切換到原始模式，無需按 Enter 即可讀取按鍵
            ch = sys.stdin.read(1)  # 讀取第一個字符
            if ch == "\033":  # 如果是轉義字符，則可能是方向鍵，繼續讀取後兩個字符
                ch += sys.stdin.read(2)  # 讀取完整的轉義序列 (例如 "\033[A" 代表向上鍵)
        finally:
            # 恢復終端設置，確保不會影響後續輸入
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def _render(self) -> None:
        """渲染當前選單狀態"""
        # 移動游標並清除舊行 (選項數 + 問題行)
        for _ in range(len(self.options) + 1):
            print(f"{_UP}{_CLR}", end="")

        # 渲染問題行
        prefix = Style.paint("?", Style.BLUE + Style.BOLD)
        question_line = Style.paint(self.question, Style.BOLD)
        print(f"{prefix} {question_line}")

        # 渲染各個選項
        for i, option in enumerate(self.options):
            is_hover = i == self.current_index
            is_picked = self.selected[i]

            # 指標符號
            ptr = Style.paint("❯", Style.CYAN) if is_hover else " "

            # 勾選框與文字顏色
            if is_picked:
                box = Style.paint("●", Style.GREEN)
                label = Style.paint(str(option), Style.CYAN if is_hover else Style.RESET)
            else:
                box = Style.paint("○", Style.GRAY)
                label = Style.paint(str(option), Style.CYAN if is_hover else Style.GRAY)

            print(f"{ptr} {box} {label}")
        sys.stdout.flush()

    def ask(self) -> List[_T]:
        """啟動互動介面"""
        # 初始占位，避免首次渲染時覆蓋先前輸出
        print(f"{_HIDE}{self.question}")
        for _ in self.options:
            print()

        try:
            while True:
                self._render()
                key = self._get_key()

                if key == "\x1b[A":  # up
                    self.current_index = (self.current_index - 1) % len(self.options)
                elif key == "\x1b[B":  # down
                    self.current_index = (self.current_index + 1) % len(self.options)
                elif key == " ":  # space
                    self.selected[self.current_index] = not self.selected[self.current_index]
                elif key in ("\r", "\n"):  # enter
                    break
                elif key == "\x03":  # Ctrl+C
                    raise KeyboardInterrupt

            # 整理結果
            chosen = [opt for i, opt in enumerate(self.options) if self.selected[i]]
            self._finish_display(chosen)
            return chosen
        finally:
            # 確保游標恢復顯示
            print(_SHOW)

    def _finish_display(self, chosen: List[_T]) -> None:
        for _ in range(len(self.options) + 1):
            print(f"{_UP}{_CLR}")

        icon = Style.paint("✔", Style.GREEN)
        summary = Style.paint(", ".join(map(str, chosen)), Style.CYAN)
        print(f"{icon} {Style.paint(self.question, Style.BOLD)} {summary}")


class SingleChoiceSelector(Generic[_T]):
    def __init__(self, question: str, options: Sequence[_T]):
        if not options:
            raise ValueError("options cannot be empty")

        self.question: str = question
        self.options: Sequence[_T] = options
        self.current_index: int = 0

    def _get_key(self) -> str:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\033":
                ch += sys.stdin.read(2)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def _render(self) -> None:
        for _ in range(len(self.options) + 1):
            print(f"{_UP}{_CLR}", end="")

        prefix = Style.paint("?", Style.BLUE + Style.BOLD)
        question_line = Style.paint(self.question, Style.BOLD)
        print(f"{prefix} {question_line}")

        for i, option in enumerate(self.options):
            is_hover = i == self.current_index
            ptr = Style.paint("❯", Style.CYAN) if is_hover else " "
            label = Style.paint(str(option), Style.CYAN if is_hover else Style.GRAY)
            print(f"{ptr} {label}")
        sys.stdout.flush()

    def ask(self) -> _T:
        print(f"{_HIDE}{self.question}")
        for _ in self.options:
            print()

        try:
            while True:
                self._render()
                key = self._get_key()

                if key == "\x1b[A":
                    self.current_index = (self.current_index - 1) % len(self.options)
                elif key == "\x1b[B":
                    self.current_index = (self.current_index + 1) % len(self.options)
                elif key in ("\r", "\n"):
                    break
                elif key == "\x03":
                    raise KeyboardInterrupt

            chosen = self.options[self.current_index]
            self._finish_display(chosen)
            return chosen
        finally:
            print(_SHOW)

    def _finish_display(self, chosen: _T) -> None:
        for _ in range(len(self.options) + 1):
            print(f"{_UP}{_CLR}")

        icon = Style.paint("✔", Style.GREEN)
        summary = Style.paint(str(chosen), Style.CYAN)
        print(f"{icon} {Style.paint(self.question, Style.BOLD)} {summary}")
