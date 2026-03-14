from .core import ClassData, Scores
from .features.distribute_groups import run_grouping
from .features.report import (
    print_all_students_report,
    print_bad_group_report,
    print_class_report,
    print_effort_report,
    print_subject_top_report,
    print_top_group_report,
    print_top_students_report,
)
from .ui import SingleChoiceSelector
from .ui.utils import clear_screen


def main() -> None:
    class_data = ClassData.from_file("data/student_scores_100_missing.csv")

    clear_screen()
    while True:
        base_mode = SingleChoiceSelector(
            "請選擇功能",
            ["分組", "報表", "退出"],
        ).ask()

        clear_screen()

        if base_mode == "分組":
            run_grouping(class_data)
        elif base_mode == "報表":
            report_mode = SingleChoiceSelector(
                "請選擇報表類型",
                [
                    "學生報告",  # print_all_students_report
                    "班級報告",  # print_class_report
                    "前 N 名學生",  # print_top_students_report
                    "努力程度報告",  # print_effort_report
                    "科目前 N 名學生",  # print_subject_top_report
                    "前 N 組報告",  # print_top_group_report
                    "不及格組別報告",  # print_bad_group_report
                    "返回上層選單",
                ],
            ).ask()

            clear_screen()

            if report_mode == "學生報告":
                print_all_students_report(class_data)
            elif report_mode == "班級報告":
                print_class_report(class_data)
            elif report_mode == "前 N 名學生":
                print_top_students_report(class_data)
            elif report_mode == "努力程度報告":
                print_effort_report(class_data)
            elif report_mode == "科目前 N 名學生":
                subject = SingleChoiceSelector(
                    "請選擇科目",
                    Scores.SUBJECTS,
                ).ask()
                print_subject_top_report(class_data, subject)
            elif report_mode == "前 N 組報告":
                print_top_group_report(class_data)
            elif report_mode == "不及格組別報告":
                print_bad_group_report(class_data)
            elif report_mode == "返回上層選單":
                clear_screen()
                continue
        elif base_mode == "退出":
            print("\nBye~")
            break


if __name__ == "__main__":
    main()
