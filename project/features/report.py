from project.core import ClassData, Student, SubjectName
from project.ui.style import Style
from project.utils import fmt_score

SEP = Style.paint("|", Style.BLUE)
LINE = Style.paint("-" * 61, Style.BLUE)
STUDENT_HEADER = f"{'姓名':6} {SEP} {'原始分數 (中/英/數)':10} {SEP} {'修正後分數':12} {SEP} {'平時表現'}"


def print_student_report(s: Student) -> None:
    raw_parts = [fmt_score(v) for v in s.scores.to_list()]
    raw_str = "/".join(raw_parts)

    fixed_parts = [fmt_score(v, Style.CYAN) for v in s.fixed_score.to_list()]
    fixed_str = "/".join(fixed_parts)

    effort_color = Style.GREEN if s.effort_ratio >= 0.9 else ""
    effort_str = f"{effort_color}{s.effort_ratio:7.1%}{Style.RESET}"

    print(f"{s.name:5} {SEP}  {raw_str}  {SEP} {fixed_str} {SEP} {effort_str}")


def print_all_students_report(data: ClassData) -> None:
    """
    列出所有學生的報告，包含姓名、原始分數、修正後分數和平時表現
    同時在底部列出各科目的平均分數，原始分數和修正後分數分開顯示
    """

    print(Style.paint(STUDENT_HEADER, Style.BOLD))
    print(LINE)

    for s in data.students:
        print_student_report(s)


def print_class_report(data: ClassData) -> None:
    # TODO : 實作列出班級整體的報告，包含學生總數、平均分數、最高分數、最低分數等資訊
    ...


def print_top_students_report(data: ClassData, top_n: int = 3) -> None:
    # TODO : 實作列出前 N 名學生的報告，依據修正後分數排序
    ...


def print_effort_report(data: ClassData) -> None:
    # TODO : 實作列出學生努力程度的報告，依據 effort_ratio 排序
    ...


def print_subject_top_report(data: ClassData, subject: SubjectName, top_n: int = 3) -> None:
    # TODO : 實作列出指定科目前 N 名學生的報告，依據該科目的修正後分數排序
    ...


def print_top_group_report(data: ClassData, top_n: int = 3) -> None:
    # TODO : 實作列出前 N 組的報告，依據組別的平均修正後分數排序
    ...


def print_bad_group_report(data: ClassData, top_n: int = 3) -> None:
    # TODO : 列出不及格組別的報告及數量，依據組別的平均修正後分數排序
    ...
