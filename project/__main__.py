from .data import global_class_data
from .features.distribute_groups import run_grouping
from .features.report import print_all_students_report
from .ui import SingleChoiceSelector


def main() -> None:
    while True:
        base_mode = SingleChoiceSelector(
            "請選擇功能",
            ["分組", ""],
        ).ask()


if __name__ == "__main__":
    main()
