# 📂 `__main__.py` 執行流程解析

> `__main__.py` ：是整個專案的**總指揮中心**。它不負責具體的數學計算，而是負責調度各個模組，按照正確的順序執行任務

## 1. 先匯入旁邊資料的檔案

```python
from .core import ClassData

# features資料夾裡的report.py檔
from .features.report import (
    print_all_students_report,
    print_class_report,
    print_ng_students_report,
    print_top_n_students_report,
)
```
* **`from .core import ClassData`： 從旁邊的 core.py 檔案裡面，把 ClassData 這個工具拿過來**
* **前面小點`.`：代表「同一個資料夾底下」**
* **`from .features.report`： 一樣的邏輯**


## 2. 核心程式碼預覽

```python
def main() -> None:
    # 步驟 1: 讀取並處理資料
    class_data = ClassData.from_file("data/student_scores_100_missing.csv")
    
    # 步驟 2: 產出各項報表
    print_all_students_report(class_data)     # 全班成績總表
    print_class_report(class_data)            # 班級統計資訊(平均/最高/最低分)
    print_top_n_students_report(class_data)   # 前 N 名排行榜
    print_ng_students_report(class_data)      # 不及格名單
```

## 執行步驟拆解

**第一階段：資料準備**
* **指令：`ClassData.from_file(...)`**
* **行為：從指定路徑讀取 CSV 檔案**
* **隱藏邏輯：**
    * **自動解析：將 `CSV` 中的每一行文字轉換為 `Student` 物件**
    * **補上分數：針對缺失值，根據班級平均與學生平時表現自動計算「修正後分數」**
    * **統計運算：同步算好全班的最高分、最低分與平均分**

**第二階段：資料視覺化**
> **當 `class_data` 物件準備就緒後，主程式 `main.py` 會依序呼叫 `features/report.py` 中的函數，將處理好的數據呈現出來**
* **全班總表**
* **班級統計**
* **優等榜單**
* **警示名單**

## 3. 程式進入點
**這一切由以下代碼觸發執行：**
```python
if __name__ == "__main__":
    main() # 依序執行上述兩個階段 
```