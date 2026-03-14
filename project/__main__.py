"""
主程式入口，負責啟動整個應用並提供一個主選單讓用戶選擇功能
"""

from .core import ClassData
from .features.report import print_all_students_report


def main() -> None:
    class_data = ClassData.from_file("data/student_scores_100_missing.csv")
    print_all_students_report(class_data)


if __name__ == "__main__":
    main()
