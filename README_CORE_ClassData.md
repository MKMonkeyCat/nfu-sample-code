# ClassData 類別說明
`ClassData` 類別用來 管理整個班級的學生資料與統計資訊

主要功能：

- 儲存班級所有學生
- 計算班級平均、最高、最低分
- 幫每個學生計算修正分數
- 依照修正後總分排序學生
- 提供報表需要的統計資料

## 一、資料結構
建立 `ClassData` 後，大致結構：
```mermaid
ClassData
├ students
├ raw_avg_scores
├ max_scores
├ min_scores
├ fixed_avg_scores
├ fixed_min_scores
├ fixed_max_scores
└ fixed_sorted_students
```
說明：
| 屬性                      | 用途     |
| ----------------------- | ------ |
| `students`              | 所有學生列表 |
| `raw_avg_scores`        | 原始平均分  |
| `max_scores`            | 原始最高分  |
| `min_scores`            | 原始最低分  |
| `fixed_avg_scores`      | 修正後平均  |
| `fixed_min_scores`      | 修正後最低  |
| `fixed_max_scores`      | 修正後最高  |
| `fixed_sorted_students` | 修正後排名  |

## 二、初始化流程 (`__init__`)
建立 `ClassData` 時會自動完成整個班級計算流程
流程如下：
```mermaid
取得學生列表
   │
   ▼
計算原始統計
(avg / min / max)
   │
   ▼
幫每個學生計算修正分
   │
   ▼
計算修正後統計
   │
   ▼
依照修正總分排序
```

## 三、計算統計資料 `_calculate_all_stats()`
這個方法負責：
```mermaid
計算
平均
最低
最高
```
並回傳
```mermaid
{
 "avg": Scores,
 "min": Scores,
 "max": Scores
}
```

## 四、修正分數流程
在` __init__` 中
```python
for student in self.students:
    student.compute_fixed_score(...)
```
意思是：
```mermaid
對每一位學生
計算補分
```
計算後：
>　student.fixed_score
就會有值

## 五、學生排序
最後會排序學生：
```python
sorted(
    self.students,
    key=lambda s: (s.fixed_total_score, s.id),
    reverse=True
)
```
排序規則：
1. 先依 **修正後總分**
2. 分數相同 → 用 **ID 排序**

排序結果：
> fixed_sorted_students

就會變成：
```mermaid
第一名
第二名
第三名
...
```

## 六、從 CSV 建立班級 (`from_file`)
這個方法用來：
> CSV檔案 → ClassData

CSV 範例：
```mermaid
id,name,chinese,english,math
A01,Tom,90,80,
A02,Amy,85,75,70
```

讀取流程：
```mermaid
打開 CSV
   │
   ▼
逐行讀取
   │
   ▼
Student.parse_student()
   │
   ▼
建立 Student
   │
   ▼
加入 students list
   │
   ▼
建立 ClassData
```

使用方式：
```python
class_data = ClassData.from_file("students.csv")
```

## 七、整個系統完整流程
```mermaid
CSV
 │
 ▼
Student.parse_student()
 │
 ▼
Student 物件
 │
 ▼
ClassData
 │
 ├ 計算平均
 ├ 計算最低
 ├ 計算最高
 ├ 修正缺考分數
 └ 排序學生
 │
 ▼
report.py
 │
 ▼
輸出報表
```

## 八、ClassData 的角色
```mermaid
Scores → 管理三科分數
Student → 管理單一學生
ClassData → 管理整個班級
report → 輸出報表
```
> `ClassData` 是 **整個系統的核心控制中心**