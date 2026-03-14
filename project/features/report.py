"""
報告模組，包含各種報告的生成函數
"""

from project.core import ClassData, Student
from project.utils import Style, fmt_score

SEP = Style.paint("|", Style.BLUE)
LINE = Style.paint("-" * 61, Style.BLUE)
STUDENT_HEADER = f"{'姓名':6} {SEP} {'原始分數 (中/英/數)':10} {SEP} {'修正後分數':12} {SEP} {'平時表現'}"


def print_student_report(s: Student) -> None:
    """
    列出單一學生的報告，包含姓名、原始分數、修正後分數和平時表現
    format demo:
    `羅志遠   |   66.0/ 59.0/ 83.0  |  66.0/ 59.0/ 83.0 |   50.0%`
    """

    # 將每個成績使用 fmt_score 格式化顏色後已 '/' 插入兩兩之間
    raw_str = "/".join(map(fmt_score, s.scores.to_list()))
    fixed_str = "/".join(map(fmt_score, s.fixed_score.to_list()))

    # 根據學生的努力程度 (effort_ratio) 決定顏色，90% 以上為綠色，否則使用預設顏色
    effort_color = Style.GREEN if s.effort_ratio >= 0.9 else ""
    effort_str = Style.paint(f"{s.effort_ratio:7.1%}", effort_color)

    # TODO 添加學生的平均分數和排名等資訊，讓報告更完整
    print(f"{s.name:5} {SEP}  {raw_str}  {SEP} {fixed_str} {SEP} {effort_str}")


def print_all_students_report(data: ClassData) -> None:
    """
    列出所有學生的報告，包含姓名、原始分數、修正後分數和平時表現
    同時在底部列出各科目的平均分數，原始分數和修正後分數分開顯示
    """

    print(Style.paint(STUDENT_HEADER, Style.BOLD))
    print(LINE)

    # 將所有學生抓出，由 `print_student_report` 統一輸出
    for s in data.students:
        print_student_report(s)


def print_class_report(data: ClassData) -> None:
    """
    列出班級整體的報告，包含每科目的平均分數、最高分數、最低分數等統計資訊
    format demo:
    `平均分數 |  70.0/ 65.0/ 80.0  |  75.0/ 70.0/ 85.0`
    `最高分數 |  95.0/ 90.0/ 98.0  | 100.0/100.0/100.0`
    `最低分數 |  40.0/ 30.0/ 50.0  |  45.0/ 35.0/ 55.0`
    """

    # TODO 根據 data 中的學生資料計算各科目的平均分、最高分和最低分，並使用 fmt_score 格式化顏色後輸出


def print_top_n_students_report(data: ClassData, n: int = 3) -> None:
    """
    列出前 N 名學生的報告，根據修正後的總分排序，包含姓名、原始分數、修正後分數和平時表現
    format demo:
    `1. 羅志遠   |   66.0/ 59.0/ 83.0  |  66.0/ 59.0/ 83.0 |   50.0%`
    `2. 林小明   |   80.0/ 85.0/ 90.0  |  85.0/ 80.0/ 95.0 |   80.0%`
    `3. 張大華   |   70.0/ 75.0/ 80.0  |  75.0/ 70.0/ 85.0 |   60.0%`
    """

    # TODO 根據 data 中的學生資料計算每個學生的修正後總分，排序後取前 N 名，並使用 print_student_report 輸出


def print_ng_students_report(data: ClassData) -> None:
    """
    列出不及格學生的報告，根據修正後的總分判斷是否不及格，包含姓名、原始分數、修正後分數和平時表現
    format demo:
    `1. 王小明   |   50.0/ 40.0/ 45.0  |  55.0/ 45.0/ 50.0 |   30.0%`
    `2. 李大華   |   40.0/ 30.0/ 35.0  |  45.0/ 35.0/ 40.0 |   20.0%`
    """

    # TODO 根據 data 中的學生資料計算每個學生的修正後總分，判斷是否不及格 (例如總分 < 60)，並使用 print_student_report 輸出
