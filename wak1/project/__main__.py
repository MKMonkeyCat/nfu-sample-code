"""
主程式入口，負責啟動整個應用並提供一個主選單讓用戶選擇功能
"""

from .core import ClassData
from .features.report import (
    print_all_students_report,
    print_class_report,
    print_ng_students_report,
    print_top_n_students_report,
)

DEBUG = False


def main() -> None:
    class_data = ClassData.from_file("data/student_scores_100_missing.csv")

    if DEBUG:
        # For print step 1 debug
        print("\n".join(map(str, class_data.students[:5])))

    print_all_students_report(class_data)
    print_class_report(class_data)
    print_top_n_students_report(class_data)
    print_ng_students_report(class_data)


if __name__ == "__main__":
    main()
