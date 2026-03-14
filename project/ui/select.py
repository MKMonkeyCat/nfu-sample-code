""""""

import sys  # 負責系統層級的操作，例如標準輸入輸出 (stdin/stdout) 與檔案描述符 (fd)
import termios  # Linux/macOS 專用的終端機控制接口，用來修改鍵盤輸入模式 (例如關閉 Enter 緩衝)
import tty  # 提供更簡便的函式來切換終端機模式 (例如將終端機設為 raw 模式)
from abc import ABC, abstractmethod  # 用來定義「抽象基底類別」，確保子類別一定要實作特定的方法
from typing import Any, Generic, List, Sequence, TypeVar

from .style import Style
from .utils import ANSI

_T = TypeVar("_T")


def _get_key() -> str:
    """讀取單個按鍵輸入，支持方向鍵和 Enter 鍵"""
    # 獲取 stdin 的 FileDescriptor (可以理解成通道編號)，一般為:
    # - 0 (stdin): 標準輸入 (通常是鍵盤)
    # - 1 (stdout): 標準輸出 (螢幕顯示)
    # - 2 (stderr): 標準錯誤 (錯誤訊息輸出)
    fd = sys.stdin.fileno()
    # 終端機底下有些設定如: [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
    # 輸入模式, 輸出模式, 控制模式, 本地模式, i速度, o速度, 特殊控制字元 等等終端本身的設定
    # 由於之後會切換到 raw 模式以便即時讀取按鍵，先在此保存之前的終端設定
    old_settings = termios.tcgetattr(fd)
    try:
        # 進入 raw 模式，這樣就不需要按 Enter 鍵就能讀取按鍵輸入
        tty.setraw(fd)
        # 讀取一個字元，對於普通按鍵會直接返回該字元
        ch = sys.stdin.read(1)
        # 處理轉義序列
        if ch == "\x1b":
            # 由於前面為 \x1b 轉役序列的開始，接下來會有兩個字元表示方向鍵
            ch += sys.stdin.read(2)
    finally:
        # 恢復終端機設定，確保不會影響後續的輸入輸出
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


class BaseSelector(ABC, Generic[_T]):
    """選單基底類別，提供共用的渲染與輸入處理邏輯，具體的選項顯示由子類實作"""

    def __init__(self, question: str, options: Sequence[_T]):
        if not options:
            raise ValueError("選項列表不能為空")

        self.question = question
        self.options = options
        self.current_index = 0  # 當前游標所在的選項索引
        self.line_count = len(options) + 1  # 選項行數 + 問題行數

    def _clear_rendered_lines(self) -> None:
        """批量清除之前渲染的內容"""
        sys.stdout.write((ANSI.UP + ANSI.CLR_LINE) * self.line_count)

    @abstractmethod
    def _render_option(self, index: int, option: _T) -> str:
        """子類需實作具體的選項顯示邏輯"""

    def _render_full_menu(self) -> None:
        """渲染整個選單，包括問題和所有選項，並根據當前狀態顯示不同的樣式"""
        prefix = Style.paint("?", Style.BLUE + Style.BOLD)
        question_line = Style.paint(self.question, Style.BOLD)

        output = [f"{prefix} {question_line}"]
        # enumerate 能同時獲取選項的索引和值，方便在渲染時根據索引決定樣式
        for i, option in enumerate(self.options):
            # 將 index 及 option 交給 `_render_option` 函數，由他生成對應的顯示字串，並加入到輸出列表中
            output.append(self._render_option(i, option))

        # output: (用 InteractiveSelector 當 demo)
        # ? 問題\n
        # ❯ 選項一\n
        # ● 選項二\n
        # \n
        sys.stdout.write("\n".join(output) + "\n")
        # 確保輸出的內容立即生效並顯示，不留在記憶體暫存中
        sys.stdout.flush()

    def _finish_display(self, result_text: str) -> None:
        """在選擇完成後清除選單並顯示結果摘要，提供視覺反饋給使用者"""
        self._clear_rendered_lines()  # 清除選單內容

        icon = Style.paint("✔", Style.GREEN)
        summary = Style.paint(result_text, Style.CYAN)
        # 顯示 選擇結果，例如：✔ 問題 選擇結果
        print(f"{icon} {Style.paint(self.question, Style.BOLD)} {summary}")

    @abstractmethod
    def ask(self) -> Any:
        """啟動選單交互，處理用戶輸入並返回選擇結果，具體的行為由子類實作"""


class InteractiveSelector(BaseSelector[_T]):
    """多選選單"""

    def __init__(self, question: str, options: Sequence[_T]):
        """初始化選單狀態，使用布林列表追蹤每個選項的選擇狀態"""

        super().__init__(question, options)  # 呼叫父類別的初始化方法
        self.selected = [False] * len(options)  # 初始化選擇狀態列表，預設為全未選擇

    def _render_option(self, index: int, option: _T) -> str:
        """
        根據選項狀態決定顯示樣式：
            - 游標所在選項顯示藍色指示符
            - 已選擇的選項顯示綠色實心圓，未選擇的顯示灰色空心圓
            - 選項文字根據是否被選中或游標所在改變
        """
        is_hover = index == self.current_index
        is_picked = self.selected[index]

        ptr = Style.paint("❯", Style.CYAN) if is_hover else " "
        box = Style.paint("●", Style.GREEN) if is_picked else Style.paint("○", Style.GRAY)

        # 決定標籤顏色，游標所在顯示藍色，已選擇的顯示綠色，其他顯示灰色
        color = Style.CYAN if is_hover else (Style.RESET if is_picked else Style.GRAY)
        label = Style.paint(str(option), color)

        # ❯ ● label
        #   ○ label
        return f"{ptr} {box} {label}"

    def ask(self) -> List[_T]:
        """透過循環處理用戶輸入，更新當前選項索引和選擇狀態，直到用戶按下 Enter 鍵確認選擇，最後返回所有被選中的選項列表"""
        # 隱藏游標，避免在選單交互過程中游標閃爍影響體驗，最後在結束時恢復顯示游標
        sys.stdout.write(ANSI.HIDE_CURSOR)
        # 預留空間
        print(f"{self.question}\n" + "\n" * len(self.options), end="")

        try:
            while True:
                # 清除之前渲染的選單內容，重新渲染整個選單以反映最新的狀態
                self._clear_rendered_lines()
                # 渲染整個選單，包括問題和所有選項，並根據當前狀態顯示不同的樣式
                self._render_full_menu()

                key = _get_key()  # 讀取用戶按鍵輸入
                if key == ANSI.KEY_UP:
                    # 往上移動游標，使用模運算實現循環移動，當到達第一個選項再按上會回到最後一個選項
                    self.current_index = (self.current_index - 1) % len(self.options)
                elif key == ANSI.KEY_DOWN:
                    # 往下移動游標，使用模運算實現循環移動，當到達最後一個選項再按下會回到第一個選項
                    self.current_index = (self.current_index + 1) % len(self.options)
                elif key == ANSI.KEY_SPACE:
                    # 切換當前游標所在選項的選擇狀態，按空格鍵可以選擇或取消選擇該選項
                    self.selected[self.current_index] = not self.selected[self.current_index]
                elif key in ANSI.KEY_ENTER:
                    break
                elif key == ANSI.KEY_CTRL_C:
                    raise KeyboardInterrupt

            chosen = [opt for i, opt in enumerate(self.options) if self.selected[i]]
            self._finish_display(", ".join(map(str, chosen)))
            return chosen
        finally:
            # 將游標搞回來
            sys.stdout.write(ANSI.SHOW_CURSOR)


# 以下部分註解請看 InteractiveSelector 的註解，邏輯類似但少了選擇狀態的切換
class SingleChoiceSelector(BaseSelector[_T]):
    """單選選單"""

    def _render_option(self, index: int, option: _T) -> str:
        """
        根據選項狀態決定顯示樣式：
            - 游標所在選項顯示藍色指示符
            - 已選擇的選項顯示綠色勾號，未選擇的顯示灰色空格
            - 選項文字根據是否被選中或游標所在改變
        """
        is_hover = index == self.current_index
        ptr = Style.paint("❯", Style.CYAN) if is_hover else " "
        label = Style.paint(str(option), Style.CYAN if is_hover else Style.GRAY)
        return f"{ptr} {label}"

    def ask(self) -> _T:
        """透過循環處理用戶輸入，更新當前選項索引，直到用戶按下 Enter 鍵確認選擇，最後返回選擇的結果"""
        sys.stdout.write(ANSI.HIDE_CURSOR)
        print(f"{self.question}\n" + "\n" * len(self.options), end="")

        try:
            while True:
                self._clear_rendered_lines()
                self._render_full_menu()

                key = _get_key()
                if key == ANSI.KEY_UP:
                    self.current_index = (self.current_index - 1) % len(self.options)
                elif key == ANSI.KEY_DOWN:
                    self.current_index = (self.current_index + 1) % len(self.options)
                elif key in ANSI.KEY_ENTER:
                    break
                elif key == ANSI.KEY_CTRL_C:
                    raise KeyboardInterrupt

            chosen = self.options[self.current_index]
            self._finish_display(str(chosen))
            return chosen
        finally:
            sys.stdout.write(ANSI.SHOW_CURSOR)
