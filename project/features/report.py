"""
報告模組，包含各種報告的生成函數
"""

from project.core import ClassData, Scores, Student
from project.utils import Style, fmt_score

SEP = Style.paint("|", Style.BLUE)
LINE = Style.paint("-" * 45, Style.BLUE)
STUDENT_HEADER = f"排名 {SEP} {'姓名':6} {SEP} {'修正後分數':12} {SEP} 平均成績"


def print_student_report(s: Student, class_data: "ClassData") -> None:
    """
    列出單一學生的報告，包含姓名、原始分數、修正後分數和平時表現與個人平均
    format demo:
    `羅志遠   |   66.0/ 59.0/ 83.0  |  66.0/ 59.0/ 83.0 |   50.0%`
    """

    # 將每個成績使用 fmt_score 格式化顏色後已 '/' 插入兩兩之間
    fixed_str = "/".join(map(fmt_score, s.fixed_score.to_list()))

    # 呼叫 core.py 裡的屬性

    avg = sum(s.fixed_score.to_list()) / 3

    # 排名

    # sorted_students = sorted(
    #   all_students,key=lambda x: sum(x.fixed_score.to_list()) / 3, reverse=True
    # )
    # rank = sorted_students.index(s) + 1

    # print(
    #    f"{s.name:5} {SEP} {raw_str} {SEP} {fixed_str} {SEP} {fmt_score(avg)} {SEP} {effort_str} {SEP} Rank:{rank}"
    # )

    # --- 計算並列排名 ---
    # 先計算每個學生的平均分數
    avg_list = [(stud, sum(stud.fixed_score.to_list()) / 3) for stud in class_data.students]
    # 依平均分數高到低排序
    avg_list.sort(key=lambda x: x[1], reverse=True)

    rank = 1
    last_score = None
    same_rank_count = 0
    student_rank = None

    for i, (stud, score) in enumerate(avg_list):
        if score == last_score:
            same_rank_count += 1
        else:
            rank = i + 1
            same_rank_count = 1
            last_score = score

        if stud == s:
            student_rank = rank
            break

    # 印出完整報告
    print(f"{student_rank:4} {SEP} {s.name:5} {SEP} {fixed_str} {SEP}    {fmt_score(avg)}")


def print_all_students_report(class_data: ClassData) -> None:
    """
    列出所有學生的報告，包含姓名、原始分數、修正後分數和平時表現
    同時在底部列出各科目的平均分數，原始分數和修正後分數分開顯示
    """

    print(Style.paint(STUDENT_HEADER, Style.BOLD))
    print(LINE)

    # 將所有學生抓出，由 `print_student_report` 統一輸出
    for s in class_data.students:
        print_student_report(s, class_data)


def print_class_report(data: ClassData) -> None:
    """
    列出班級整體的報告，包含每科目的平均分數、最高分數、最低分數等統計資訊
    format demo:
    `平均分數 |  70.0/ 65.0/ 80.0  |  75.0/ 70.0/ 85.0`
    `最高分數 |  95.0/ 90.0/ 98.0  | 100.0/100.0/100.0`
    `最低分數 |  40.0/ 30.0/ 50.0  |  45.0/ 35.0/ 55.0`
    """

    print("\n" + Style.BOLD + "班級平均,最高及最低分數 (Fixed Scores)" + Style.RESET)

    def fmt_scores(scores: Scores[float]):
        return f"{fmt_score(scores.chinese)} {fmt_score(scores.english)} {fmt_score(scores.math)}"

    print(f"{'Average':>16} " + fmt_scores(data.fixed_avg_scores))
    print(f"{'max':>16} " + fmt_scores(data.fixed_max_scores))
    print(f"{'min':>16} " + fmt_scores(data.fixed_min_scores))


def print_top_n_students_report(class_data: ClassData, n: int = 3) -> None:
    """
    列出前 N 名學生的報告，根據修正後的總分排序，包含姓名、原始分數、修正後分數和平時表現
    """
    sorted_students = sorted(class_data.students, key=lambda s: s.fixed_total_score, reverse=True)

    top_students = sorted_students[:n]

    print(f"\n班級前 {n} 名排行榜")

    for s in top_students:
        print_student_report(s, class_data)

    print(LINE)


def print_ng_students_report(class_data: ClassData) -> None:
    """
    列出不及格學生的報告，根據修正後的總分判斷是否不及格，包含姓名、原始分數、修正後分數和平時表現
    format demo:
    `1. 王小明   |   50.0/ 40.0/ 45.0  |  55.0/ 45.0/ 50.0 |   30.0%`
    `2. 李大華   |   40.0/ 30.0/ 35.0  |  45.0/ 35.0/ 40.0 |   20.0%`
    """
    fail_count = 0

    for s in class_data.students:
        if s.fixed_average < 60:
            fail_count = fail_count + 1

    print("不及格學生數量:", fail_count)
