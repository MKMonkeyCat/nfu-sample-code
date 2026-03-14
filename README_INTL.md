# README_INTL（實務使用版）

這份文件以「怎麼使用」為主，重點放在：

1. 可以直接呼叫的公開變數、函式、類別
2. 實際使用流程與範例
3. 目前可用功能與尚未完成功能

本文件不展示內部實作細節（例如底線開頭的私有方法）。

---

## 1. 專案用途

此專案用來處理學生分數資料，提供：

1. CSV 讀取與學生資料建模
2. 缺值分數修正
3. 班級統計資料
4. 終端機互動式選單元件
5. 報表輸出（目前已有學生清單報表）

---

## 2. 快速開始

### 2.1 用 CLI 執行

在專案根目錄執行：

```bash
python -m project
```

目前狀態：

1. 主選單會出現
2. 但主流程尚未完整串接到所有功能

### 2.2 在程式中直接使用

```python
from project.data import global_class_data
from project.features.report import print_all_students_report

print_all_students_report(global_class_data)
```

---

## 3. 公開 API 一覽（建議優先使用）

## 3.1 資料入口：project.data

### 函式 get_data() -> list[Student]

用途：讀取 data/student_scores_100_missing.csv，回傳學生物件列表。

參數：無

回傳：

1. list[Student]

範例：

```python
from project.data import get_data

students = get_data()
print(len(students))
print(students[0].name)
```

### 變數 global_class_data: ClassData

用途：已載入完成的全班資料物件（可直接拿來做統計與報表）。

範例：

```python
from project.data import global_class_data

print(global_class_data.fixed_avg_scores.to_list())
```

### 變數 global_student_data: list[Student]

用途：全班學生列表（等同 global_class_data.students）。

範例：

```python
from project.data import global_student_data

for s in global_student_data[:3]:
    print(s.id, s.name)
```

---

## 3.2 核心資料模型：project.core

## 類別 Scores

用途：表示三科分數（國文、英文、數學）。

### 建構參數

1. chinese: float 或 None
2. english: float 或 None
3. math: float 或 None

### 常用公開成員

1. chinese / english / math
2. to_list() -> list
3. get_by_name(name) -> 單科分數，name 可為 chinese、english、math
4. from_iterable(values) -> 由可迭代物件建立 Scores

範例：

```python
from project.core import Scores

scores = Scores(80.0, 75.5, 90.0)
print(scores.to_list())
print(scores.get_by_name("english"))
```

## 類別 Student

用途：表示單一學生。

### 建構參數

1. id\_: str，學號
2. name: str，姓名
3. chinese: float 或 None
4. english: float 或 None
5. math: float 或 None
6. effort_ratio: float（關鍵字參數，預設 0.5）

### 常用公開成員

1. id
2. name
3. scores（原始分數，Scores）
4. effort_ratio
5. fixed_score（修正後分數，Scores）
6. fixed_total_score（修正後總分，property）
7. parse_student(line) -> Student
8. compute_fixed_score(avg_scores, min_scores) -> None

範例 1：手動建立 Student

```python
from project.core import Student

s = Student("A01", "王小明", 88.0, None, 70.0, effort_ratio=0.8)
print(s.name)
print(s.scores.to_list())
```

範例 2：由 CSV 一行建立 Student

```python
from project.core import Student

line = "S001,王小明,88,,70"
s = Student.parse_student(line)
print(s.id, s.name, s.scores.to_list())
```

範例 3：計算缺值修正後分數

```python
from project.core import Student, Scores

s = Student("S002", "陳小華", None, 65.0, None, effort_ratio=0.6)
avg_scores = Scores(78.0, 72.0, 75.0)
min_scores = Scores(50.0, 40.0, 45.0)

s.compute_fixed_score(avg_scores, min_scores)
print(s.fixed_score.to_list())
print(s.fixed_total_score)
```

## 類別 ClassData

用途：封裝班級學生、統計值、分組結果。

### 建構參數

1. students: list[Student]

### 常用公開成員

1. students
2. raw_avg_scores / max_scores / min_scores
3. fixed_avg_scores / fixed_max_scores / fixed_min_scores
4. groups（可讀可寫）
5. get_group_of_student(student_id) -> int 或 None
6. get_students_in_group(group_index) -> list[Student]

範例 1：建立 ClassData 並查看統計

```python
from project.data import get_data
from project.core import ClassData

cls_data = ClassData(get_data())
print("原始平均:", cls_data.raw_avg_scores.to_list())
print("修正後平均:", cls_data.fixed_avg_scores.to_list())
```

範例 2：設定分組並查詢

```python
from project.data import get_data
from project.core import ClassData

students = get_data()
cls_data = ClassData(students)

cls_data.groups = [students[:3], students[3:6], students[6:9]]

target = students[0]
group_idx = cls_data.get_group_of_student(target.id)
print(target.name, "在第", group_idx, "組")

members = cls_data.get_students_in_group(group_idx)
print([m.name for m in members])
```

---

## 3.3 報表功能：project.features.report

### 可用函式

1. print_student_report(s: Student) -> None
2. print_all_students_report(data: ClassData) -> None

範例：

```python
from project.data import global_class_data
from project.features.report import print_all_students_report

print_all_students_report(global_class_data)
```

### 尚未完成函式（目前為 TODO）

1. print_class_report
2. print_top_students_report
3. print_effort_report
4. print_subject_top_report
5. print_top_group_report
6. print_bad_group_report

---

## 3.4 分組功能：project.features.distribute_groups

### 函式 run_grouping(data: ClassData) -> None

用途：啟動分組模式選單。

參數：

1. data: ClassData

範例：

```python
from project.data import global_class_data
from project.features.distribute_groups import run_grouping

run_grouping(global_class_data)
```

注意：目前只有選單與模式分支，尚未真正產生分組結果。

---

## 3.5 顯示輔助工具：project.utils

### 函式 fmt_score(v: float | None, color: str = "") -> str

用途：把分數轉成固定格式字串，並加上顏色。

參數：

1. v：分數或 None
2. color：指定顏色碼；若不給，會依分數區間自動上色

範例：

```python
from project.utils import fmt_score

print(fmt_score(95.0))
print(fmt_score(58.5))
print(fmt_score(None))
```

---

## 3.6 終端互動元件：project.ui.select

## 類別 SingleChoiceSelector

用途：單選題（上下移動 + Enter 確認）。

### 建構參數

1. question: str
2. options: Sequence[T]，不可為空

### 方法

1. ask() -> T

範例：

```python
from project.ui.select import SingleChoiceSelector

mode = SingleChoiceSelector("請選擇模式", ["分組", "報表", "離開"]).ask()
print("你選了:", mode)
```

## 類別 InteractiveSelector

用途：多選題（上下移動 + Space 勾選 + Enter 確認）。

### 建構參數

1. question: str
2. options: Sequence[T]

### 方法

1. ask() -> list[T]

範例：

```python
from project.ui.select import InteractiveSelector

chosen = InteractiveSelector("請選擇科目", ["國文", "英文", "數學"]).ask()
print(chosen)
```

---

## 4. 常見使用情境

### 情境 1：只想快速印出全班報表

```python
from project.data import global_class_data
from project.features.report import print_all_students_report

print_all_students_report(global_class_data)
```

### 情境 2：自己載入資料後做統計

```python
from project.data import get_data
from project.core import ClassData

data = ClassData(get_data())
print(data.fixed_avg_scores.to_list())
print(data.fixed_max_scores.to_list())
print(data.fixed_min_scores.to_list())
```

### 情境 3：自訂小型資料做功能測試

```python
from project.core import Student, ClassData

students = [
    Student("T01", "A", 80, None, 70, effort_ratio=0.7),
    Student("T02", "B", 60, 65, None, effort_ratio=0.5),
    Student("T03", "C", None, 90, 88, effort_ratio=0.9),
]

cls = ClassData(students)
print(cls.fixed_avg_scores.to_list())
```

---

## 5. 目前狀態（務實版）

### 已可穩定使用

1. CSV 讀取
2. 學生/班級資料建模
3. 缺值分數修正
4. 基本班級統計
5. 單選/多選終端互動
6. 全班學生清單報表

### 尚未完成

1. 主程式選單完整串接
2. 分組演算法
3. 大部分進階報表函式

如果你接下來要實作功能，建議順序：

1. 先完成 main 選單流程
2. 再完成 run_grouping 的一種可用模式（例如隨機分組）
3. 最後補齊 report.py 的 TODO
