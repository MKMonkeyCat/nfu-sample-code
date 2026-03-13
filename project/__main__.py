from typing import Optional

from project.core import ClassData
from project.data import global_class_data


def print_report(data: ClassData):
    # 標題與分隔線
    print(f"{'姓名':<11} | {'原始分數 (中/英/數)':<15} | {'修正後分數':<17} | {'平時表現'}")
    print("-" * 80)

    for s in data.students:

        def fmt(v: Optional[float]) -> str:
            return f"{v:5.1f}" if v is not None else "---.-"

        raw_str = "/".join(fmt(v) for v in s.scores.to_list())
        fixed_str = "/".join(fmt(v) for v in s.fixed_score.to_list())

        print(f"{s.name:<10} | {raw_str:<22} | {fixed_str:<22} | {s.effort_ratio:7.1%}")

    print("-" * 80)


if __name__ == "__main__":
    print_report(global_class_data)
