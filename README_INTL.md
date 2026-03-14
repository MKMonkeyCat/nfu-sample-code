# README_INTL

這份文件是「重構後版本」的實務使用指南，專注於：

1. 目前可直接使用的功能
2. 公開 API 與常見呼叫方式
3. 現階段尚未實作完成的區塊

不說明過多內部細節，目標是讓你可以快速上手、快速定位下一步開發點。

---

## 1. 專案簡介

本專案用來處理學生分數資料（CSV），提供：

1. 學生與班級資料模型 (`Student`, `Scores`, `ClassData`)
2. 缺值分數修正機制（依平均、最低分與努力比例推估）
3. CLI 互動選單（單選/多選，方向鍵操作）
4. 報表框架與一個已完成報表（全班學生報表）
5. 分組功能入口（目前流程已建、演算法待實作）

---

## 2. 快速開始

### 2.1 執行主程式

在專案根目錄執行：

```bash
python -m project
```

主程式流程：

1. 讀取 `data/student_scores_100_missing.csv`
2. 建立 `ClassData`
3. 顯示主選單（分組 / 報表 / 退出）

### 2.2 直接在 Python 中使用

```python
from project.core import ClassData
from project.features.report import print_all_students_report

data = ClassData.from_file("data/student_scores_100_missing.csv")
print_all_students_report(data)
```

---

## 3. 專案結構（重構後）

```text
project/
  __main__.py              # CLI 入口
  core.py                  # Scores / Student / ClassData
  utils.py                 # 通用格式化工具 (fmt_score)
  features/
    report.py              # 各式報表（多數為 TODO）
    distribute_groups.py   # 分組流程入口（演算法 TODO）
  ui/
    select.py              # SingleChoiceSelector / InteractiveSelector
    style.py               # ANSI 樣式
    utils.py               # ANSI 常數與 clear_screen()
data/
  student_scores_100_missing.csv
```

---

## 4. 公開 API 重點

## 4.1 `project.core`

### `Scores`

用途：封裝三科分數（`chinese`, `english`, `math`）。

常用成員：

1. `Scores.SUBJECTS`
2. `get_by_name(name)`
3. `to_list()`
4. `from_iterable(values)`

範例：

```python
from project.core import Scores

s = Scores(88.0, 76.5, 91.0)
print(s.to_list())
print(s.get_by_name("english"))
```

### `Student`

用途：表示單一學生與其原始/修正後分數。

建構參數：

1. `id_`: 學號
2. `name`: 姓名
3. `chinese`, `english`, `math`: 分數（可為 `None`）
4. `effort_ratio`: 努力比例，預設 `0.5`

常用成員：

1. `id`, `name`
2. `scores`（原始分數）
3. `fixed_score`（修正後分數）
4. `fixed_total_score`（property）
5. `parse_student(line)`
6. `compute_fixed_score(avg_scores, min_scores)`

### `ClassData`

用途：封裝整班資料、統計結果、分組結果。

常用成員：

1. `students`
2. `raw_avg_scores`, `max_scores`, `min_scores`
3. `fixed_avg_scores`, `fixed_max_scores`, `fixed_min_scores`
4. `groups`（可設置，會同步更新查詢索引）
5. `get_group_of_student(student_id)`
6. `get_students_in_group(group_index)`
7. `from_file(path)`

範例：

```python
from project.core import ClassData

data = ClassData.from_file("data/student_scores_100_missing.csv")

print("原始平均:", data.raw_avg_scores.to_list())
print("修正後平均:", data.fixed_avg_scores.to_list())
```

---

## 4.2 `project.features.report`

### 目前可用

1. `print_student_report(s)`
2. `print_all_students_report(data)`

### 目前為 TODO

1. `print_class_report(data)`
2. `print_top_students_report(data, top_n=3)`
3. `print_effort_report(data)`
4. `print_subject_top_report(data, subject, top_n=3)`
5. `print_top_group_report(data, top_n=3)`
6. `print_bad_group_report(data, top_n=3)`

---

## 4.3 `project.features.distribute_groups`

### `run_grouping(data)`

功能：啟動分組模式選單。

目前狀態：

1. 已有分組模式選單流程
2. 尚未實作真正分組演算法
3. 目前會顯示「分組功能尚未實作」

---

## 4.4 `project.ui`

### `SingleChoiceSelector`

單選元件（上/下鍵移動，Enter 確認）。

### `InteractiveSelector`

多選元件（上/下鍵移動，Space 勾選，Enter 確認）。

範例：

```python
from project.ui import SingleChoiceSelector, InteractiveSelector

mode = SingleChoiceSelector("請選擇模式", ["報表", "分組", "退出"]).ask()
subjects = InteractiveSelector("請選擇科目", ["chinese", "english", "math"]).ask()

print(mode)
print(subjects)
```

---

## 4.5 `project.utils`

### `fmt_score(v, color="")`

用途：將分數格式化為固定寬度並可上色；`None` 會顯示為 `---.-`。

---

## 5. CLI 目前行為

`python -m project` 進入主程式後：

1. `分組`
   目前只進入模式選單，尚未產生實際分組結果。
2. `報表`
   只有「學生報告」可正常輸出，其餘選項是預留函式。
3. `退出`
   正常結束程式。

---

## 6. 平台與相依說明

1. 使用 ANSI 控制碼與 `termios/tty` 讀取按鍵。
2. 互動選單適合 Linux/macOS 終端環境。
3. 若在不支援 `termios` 的環境（例如部分 Windows 設定）執行，可能需要額外相容層。

---

## 7. 建議開發順序（依現在版本）

1. 先完成 `distribute_groups.py` 至少一種分組模式（例如隨機分組）
2. 補齊 `report.py` 的 TODO 報表
3. 再把分組結果整合進報表（如前 N 組、不及格組別）

---

## 8. 最小可用範例

```python
from project.core import ClassData
from project.features.report import print_all_students_report

def main() -> None:
    data = ClassData.from_file("data/student_scores_100_missing.csv")
    print_all_students_report(data)

if __name__ == "__main__":
    main()
```
