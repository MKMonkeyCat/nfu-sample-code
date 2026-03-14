"""
分組功能的實作
"""

from project.core import ClassData
from project.ui.select import SingleChoiceSelector


def run_grouping(data: ClassData) -> None:
    if not data.students:
        print("沒有學生資料可供分組")
        return

    group_mode = SingleChoiceSelector(
        "請選擇分組模式",
        [
            "依據修正後分數進行分組",
            "依據努力程度進行分組",
            "綜合考量分數和努力程度進行分組",
            "隨機分組",
        ],
    ).ask()

    # TODO: 實作分組邏輯
    # 依據學生的 fixed_score 進行分組，確保每組的平均分數盡可能接近
    # 可以使用簡單的貪心算法，或是更複雜的分割演算法來達成
    # 例如：將學生按照 fixed_score 排序，然後依序分配到不同的組別中，確保每組的總分數盡可能平衡
    # 也可以考慮學生的努力程度 (effort_ratio) 來進行分組，確保每組中都有不同努力程度的學生
    # 分組結果可以以列表的形式輸出，每個列表代表一個組別，裡面包含該組的學生姓名和分數等資訊
    # 最後可以印出每組的平均分數和學生名單，讓使用者了解分組結果

    if group_mode == "依據修正後分數進行分組":
        ...
    elif group_mode == "依據努力程度進行分組":
        ...
    elif group_mode == "綜合考量分數和努力程度進行分組":
        ...
    elif group_mode == "隨機分組":
        ...

    print("分組功能尚未實作")
