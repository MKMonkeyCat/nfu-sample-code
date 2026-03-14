# 專案統整文件（README_INTL）

本文件依據目前程式碼實作整理，涵蓋：

1. 專案整體架構
2. 各檔案功能
3. 各模組 / 類別 / 函式功能與參數
4. 目前已完成與待實作項目

---

## 1. 專案架構總覽

```text
nfu-sample-code/
├─ README.md
├─ README_INTL.md
├─ data/
│  └─ student_scores_100_missing.csv
└─ project/
	 ├─ __init__.py
	 ├─ __main__.py
	 ├─ core.py
	 ├─ data.py
	 ├─ utils.py
	 ├─ features/
	 │  ├─ distribute_groups.py
	 │  └─ report.py
	 └─ ui/
			├─ __init__.py
			├─ select.py
			└─ style.py
```

### 執行流程（目前版本）

1. 以 `python -m project` 執行 `project/__main__.py`
2. 載入 `project/data.py`，建立全域 `ClassData`（讀取 CSV + 計算修正分數）
3. 顯示互動式單選選單（`SingleChoiceSelector`）
4. 目前主程式尚未把選單結果接到實際功能（分組/報表流程未串接完成）

---

## 2. 檔案功能對照

### `project/__main__.py`

- 入口點 `main()`。
- 建立主選單（目前選項：`["分組", ""]`）。
- 尚未依選項呼叫 `run_grouping` 或 `print_all_students_report`。

### `project/__init__.py`

- 套件匯出入口。
- 匯出 `Student`、`get_data`、`global_class_data`。

### `project/core.py`

- 核心資料模型與統計邏輯。
- 定義：`Scores`、`Student`、`ClassData`。
- 包含缺值分數修正規則與班級統計計算。

### `project/data.py`

- CSV 載入邏輯。
- 產生全域資料：`global_class_data` 與 `global_student_data`。

### `project/utils.py`

- 提供分數格式化函式 `fmt_score`。
- 自動依分數區間上色（不及格、80+、90+）。

### `project/features/distribute_groups.py`

- 分組功能入口 `run_grouping(data)`。
- 目前只完成分組模式選單，實際分組演算法未實作。

### `project/features/report.py`

- 已完成：`print_student_report`、`print_all_students_report`（列印學生清單）。
- 未完成：班級總覽、前 N 名、努力程度、科目前 N 名、組別相關報表。

### `project/ui/style.py`

- ANSI 色彩/樣式常數與 `Style.paint`。

### `project/ui/select.py`

- 終端互動選單元件：
  - `InteractiveSelector`（可多選）
  - `SingleChoiceSelector`（單選）
- 支援方向鍵、空白鍵（多選）、Enter、Ctrl+C。

### `project/ui/__init__.py`

- 將 `select` 與 `style` 中符號以 `*` 匯出。

---

## 3. 模組 / 類別 / 函式與參數

## 3.1 `project/core.py`

### 型別與常數

- `SubjectName = Literal["chinese", "english", "math"]`
  - 科目名稱限定。
- `FIXED_SCORE_SPACE = 10`
  - 缺值修正時，最多可高於班平均的額外空間（上限保護）。

### 類別 `Scores[_T]`

用途：封裝三科分數（國文、英文、數學），支援泛型（可放 `float` 或 `Optional[float]`）。

#### 屬性

- `SUBJECTS: Sequence[SubjectName] = ("chinese", "english", "math")`
- `chinese: _T`
- `english: _T`
- `math: _T`

#### 方法

1. `__init__(self, chinese: _T, english: _T, math: _T) -> None`

- 功能：建立三科分數容器。
- 參數：
  - `chinese`：國文分數
  - `english`：英文分數
  - `math`：數學分數

2. `get_by_name(self, name: SubjectName) -> _T`

- 功能：用科目名稱取得分數。
- 參數：
  - `name`：`"chinese" | "english" | "math"`
- 例外：名稱非法時丟出 `ValueError`。

3. `from_iterable(cls, values: Iterable[_T]) -> Scores`

- 功能：由可迭代資料建立 `Scores`。
- 參數：
  - `values`：需提供三個值（依序對應中/英/數）。

4. `to_list(self) -> List[_T]`

- 功能：回傳 `[chinese, english, math]`。

5. `__repr__(self) -> str`

- 功能：提供除錯用字串表示。

### 類別 `Student`

用途：代表單一學生，包含原始分數、努力比率與修正後分數。

#### 屬性

- `id: str`：學號
- `name: str`：姓名
- `scores: Scores[Optional[float]]`：原始分數（可缺值）
- `effort_ratio: float`：平時努力比率
- `fixed_score: Scores[float]`：修正後分數（由計算流程填入）

#### 方法與屬性

1. `__init__(self, id_: str, name: str, chinese: Optional[float], english: Optional[float], math: Optional[float], *, effort_ratio: float = 0.5) -> None`

- 功能：建立學生資料。
- 參數：
  - `id_`：學號
  - `name`：姓名
  - `chinese` / `english` / `math`：原始分數，允許 `None`
  - `effort_ratio`：缺值修正偏向係數（預設 `0.5`）

2. `fixed_total_score(self) -> float`（property）

- 功能：回傳修正後三科總分。

3. `parse_student(cls, line: str) -> Student`

- 功能：解析一行 CSV 成學生物件。
- 參數：
  - `line`：格式類似 `id,name,chinese,english,math`

4. `compute_fixed_score(self, avg_scores: Scores[float], min_scores: Scores[float]) -> None`

- 功能：對缺值科目進行修正。
- 參數：
  - `avg_scores`：班級各科平均（原始）
  - `min_scores`：班級各科最低（原始）
- 規則摘要：
  - 若原始分數存在，直接使用。
  - 若缺值：`val = min + (avg - min) * effort_ratio`
  - 最終夾限：`0 <= val <= min(avg + FIXED_SCORE_SPACE, 100)`

### 類別 `ClassData`

用途：封裝班級學生資料、統計值與分組狀態。

#### 屬性

- `students: List[Student]`
- `raw_avg_scores: Scores[float]`
- `max_scores: Scores[float]`
- `min_scores: Scores[float]`
- `fixed_avg_scores: Scores[float]`
- `fixed_max_scores: Scores[float]`
- `fixed_min_scores: Scores[float]`
- `_groups: List[List[Student]]`
- `_groups_map: dict[str, int]`（學生 ID -> 組別索引）

#### 方法與參數

1. `__init__(self, students: List[Student]) -> None`

- 功能：建立班級資料並自動計算統計值與修正分數。
- 參數：
  - `students`：學生列表

2. `_generate_stat_scores(self, stat_func: Callable[[Sequence[float]], float]) -> Scores[float]`

- 功能：針對原始分數（略過 `None`）計算每科統計。
- 參數：
  - `stat_func`：統計函式（例如平均、最大、最小）

3. `_generate_fixed_stat_scores(self, stat_func: Callable[[Sequence[float]], float]) -> Scores[float]`

- 功能：針對修正後分數計算每科統計。
- 參數：
  - `stat_func`：統計函式

4. `_calc_average(data: Sequence[float]) -> float`（staticmethod）

- 功能：計算平均值；空資料回傳 `0`。
- 參數：
  - `data`：數值序列

5. `_apply_score_fixing(self) -> None`

- 功能：對所有學生執行 `compute_fixed_score`。

6. `groups(self) -> List[List[Student]]`（property）

- 功能：取得目前分組結果。

7. `groups(self, groups: List[List[Student]]) -> None`（setter）

- 功能：設定分組並同步更新 `_groups_map`。
- 參數：
  - `groups`：每組學生列表

8. `get_group_of_student(self, student_id: str) -> Optional[int]`

- 功能：查詢學生所在組別索引。
- 參數：
  - `student_id`：學號

9. `get_students_in_group(self, group_index: int) -> List[Student]`

- 功能：取得指定組別學生。
- 參數：
  - `group_index`：組別索引
- 例外：索引超界時丟出 `ValueError`。

---

## 3.2 `project/data.py`

### 函式

1. `get_data() -> list[Student]`

- 功能：讀取 `data/student_scores_100_missing.csv` 並回傳學生列表。
- 流程：
  - 跳過標題列
  - 每列呼叫 `Student.parse_student`

### 模組層級變數

1. `global_class_data = ClassData(get_data())`

- 功能：初始化全域班級資料（含統計與修正分數）。

2. `global_student_data = global_class_data.students`

- 功能：提供全域學生清單快捷存取。

---

## 3.3 `project/utils.py`

### 函式

1. `fmt_score(v: Optional[float], color: str = "") -> str`

- 功能：格式化顯示分數，並依區間決定顏色。
- 參數：
  - `v`：分數或 `None`
  - `color`：指定色碼（若空字串則啟用自動配色）
- 行為：
  - `None` -> 顯示 `---.-`（灰色）
  - `< 60` -> 紅色
  - `>= 80` -> 黃色
  - `>= 90` -> 綠色

---

## 3.4 `project/features/distribute_groups.py`

### 函式

1. `run_grouping(data: ClassData) -> None`

- 功能：分組功能入口，先顯示分組模式選單。
- 參數：
  - `data`：班級資料
- 目前狀態：
  - 已完成「無資料防呆」與「模式選擇」。
  - 分組演算法尚未實作（4 個模式分支皆為占位）。

---

## 3.5 `project/features/report.py`

### 常數

- `SEP`：藍色分隔符 `|`
- `LINE`：藍色底線
- `STUDENT_HEADER`：學生報表標題列

### 函式

1. `print_student_report(s: Student) -> None`

- 功能：列印單一學生（原始分數 / 修正後分數 / 努力比例）。
- 參數：
  - `s`：學生物件

2. `print_all_students_report(data: ClassData) -> None`

- 功能：列印全班學生清單。
- 參數：
  - `data`：班級資料
- 備註：註解提到底部統計摘要，但目前程式尚未實作該段輸出。

3. `print_class_report(data: ClassData) -> None`

- 功能：班級整體報告。
- 參數：
  - `data`：班級資料
- 目前狀態：`TODO`。

4. `print_top_students_report(data: ClassData, top_n: int = 3) -> None`

- 功能：前 N 名學生報告。
- 參數：
  - `data`：班級資料
  - `top_n`：名次數量（預設 3）
- 目前狀態：`TODO`。

5. `print_effort_report(data: ClassData) -> None`

- 功能：努力程度報告。
- 參數：
  - `data`：班級資料
- 目前狀態：`TODO`。

6. `print_subject_top_report(data: ClassData, subject: SubjectName, top_n: int = 3) -> None`

- 功能：指定科目前 N 名報告。
- 參數：
  - `data`：班級資料
  - `subject`：科目名稱（`chinese` / `english` / `math`）
  - `top_n`：名次數量（預設 3）
- 目前狀態：`TODO`。

7. `print_top_group_report(data: ClassData, top_n: int = 3) -> None`

- 功能：前 N 組報告。
- 參數：
  - `data`：班級資料
  - `top_n`：組別數量（預設 3）
- 目前狀態：`TODO`。

8. `print_bad_group_report(data: ClassData, top_n: int = 3) -> None`

- 功能：不及格組別報告。
- 參數：
  - `data`：班級資料
  - `top_n`：組別數量（預設 3）
- 目前狀態：`TODO`。

---

## 3.6 `project/ui/style.py`

### 類別 `Style`

用途：集中管理 ANSI 樣式碼。

#### 常數

- `BLUE`
- `CYAN`
- `GREEN`
- `GRAY`
- `YELLOW`
- `RED`
- `RESET`
- `BOLD`

#### 方法

1. `paint(text: str, style_code: str) -> str`（staticmethod）

- 功能：將文字套上 ANSI 樣式並補上重置碼。
- 參數：
  - `text`：要上色文字
  - `style_code`：樣式碼

---

## 3.7 `project/ui/select.py`

### 類別 `InteractiveSelector[_T]`（多選）

#### 建構

1. `__init__(self, question: str, options: Sequence[_T])`

- 功能：建立多選選單。
- 參數：
  - `question`：題目文字
  - `options`：選項序列

#### 方法

1. `_get_key(self) -> str`

- 功能：在 raw mode 讀取按鍵（含方向鍵 escape sequence）。

2. `_render(self) -> None`

- 功能：重繪選單 UI（清行、顯示游標位置、顯示勾選狀態）。

3. `ask(self) -> List[_T]`

- 功能：啟動互動流程，回傳所有勾選選項。
- 操作鍵：
  - `↑/↓`：移動
  - `Space`：切換勾選
  - `Enter`：確認
  - `Ctrl+C`：中止

4. `_finish_display(self, chosen: List[_T]) -> None`

- 功能：結束時清理畫面並顯示摘要。

### 類別 `SingleChoiceSelector[_T]`（單選）

#### 建構

1. `__init__(self, question: str, options: Sequence[_T])`

- 功能：建立單選選單。
- 參數：
  - `question`：題目文字
  - `options`：選項序列（不可為空）
- 例外：`options` 為空時丟 `ValueError`。

#### 方法

1. `_get_key(self) -> str`

- 功能：讀取按鍵。

2. `_render(self) -> None`

- 功能：重繪單選選單。

3. `ask(self) -> _T`

- 功能：啟動互動並回傳目前選中的單一項目。

4. `_finish_display(self, chosen: _T) -> None`

- 功能：結束時顯示最終選擇摘要。

---

## 3.8 其他匯出模組

### `project/ui/__init__.py`

- `from .select import *`
- `from .style import *`
- 功能：讓外部可直接從 `project.ui` 取用 UI 相關符號。

### `project/__init__.py`

- `from .core import Student`
- `from .data import get_data, global_class_data`
- 功能：提供套件頂層常用匯出。

---

## 4. 完成度與目前限制

### 已完成

1. CSV 解析與學生模型
2. 缺值分數修正與班級統計
3. CLI 色彩化顯示工具
4. CLI 單選/多選互動元件
5. 學生清單報表（基本輸出）

### 待完成

1. `project/__main__.py` 主選單流程串接
2. `project/features/distribute_groups.py` 分組演算法
3. `project/features/report.py` 多數報表函式（`TODO`）
4. 分組結果回寫 `ClassData.groups` 並輸出組別報表

---

## 5. 建議下一步（可直接作為開發任務）

1. 補齊 `main()` 選單流程：分組、全部學生報表、班級報表、離開。
2. 在 `run_grouping` 先實作「隨機分組」作為最小可用版本。
3. 補上 `print_class_report`（平均、最高、最低、缺值修正前後對照）。
4. 新增簡單測試：
   - `Student.parse_student`
   - `Student.compute_fixed_score`
   - `ClassData` 統計結果
