from typing import Optional

from project.core import ClassData, Scores
from project.data import global_class_data

# ANSI 顏色定義
CLR_RESET = "\033[0m"
CLR_BOLD = "\033[1m"
CLR_GRAY = "\033[90m"
CLR_CYAN = "\033[36m"
CLR_YELLOW = "\033[33m"
CLR_RED = "\033[31m"  # 用於不及格
CLR_GREEN = "\033[32m"  # 用於表現優異
CLR_BLUE = "\033[34m"  # 用於表格格線


def fmt(v: Optional[float], color: str = "") -> str:
    if v is None:
        return f"{CLR_GRAY}---.-{CLR_RESET}"

    display_color = color
    if not color:
        if v < 60:
            display_color = CLR_RED
        elif v >= 90:
            display_color = CLR_GREEN
        elif v >= 80:
            display_color = CLR_YELLOW

    text = f"{v:5.1f}"
    return f"{display_color}{text}{CLR_RESET}" if display_color else text


def print_report(data: ClassData):
    sep = f"{CLR_BLUE}|{CLR_RESET}"
    line = f"{CLR_BLUE}{'-' * 80}{CLR_RESET}"

    header = f"{'姓名':<11} {sep} {'原始分數 (中/英/數)':<18} {sep} {'修正後分數':<20} {sep} {'平時表現'}"

    print(f"{CLR_BOLD}{header}{CLR_RESET}")
    print(line)

    for s in data.students:
        raw_parts = [fmt(v) for v in s.scores.to_list()]
        raw_str = "/".join(raw_parts)

        fixed_parts = [fmt(v, CLR_CYAN) for v in s.fixed_score.to_list()]
        fixed_str = "/".join(fixed_parts)

        effort_color = CLR_GREEN if s.effort_ratio >= 0.9 else ""
        effort_str = f"{effort_color}{s.effort_ratio:7.1%}{CLR_RESET}"

        print(f"{s.name:10} {sep} {raw_str} {sep} {fixed_str} {sep} {effort_str}")

    print(line)

    raw_avg_parts = [fmt(data.raw_avg_scores.get_by_name(sub)) for sub in Scores.SUBJECTS]
    raw_avg_str = "/".join(raw_avg_parts)

    fixed_avg_parts = [fmt(data.fixed_avg_scores.get_by_name(sub), CLR_YELLOW) for sub in Scores.SUBJECTS]
    fixed_avg_str = "/".join(fixed_avg_parts)

    footer_label = f"{CLR_BOLD}平均分數{CLR_RESET}"
    print(f"{footer_label:18} {sep} {raw_avg_str} {sep} {fixed_avg_str} {sep}")


if __name__ == "__main__":
    print_report(global_class_data)
