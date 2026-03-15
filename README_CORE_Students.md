# Student 類別說明

`Student` 類別用來表示 **一位學生的完整資訊**，包含：

- 學生 ID
- 姓名
- 三科原始成績
- 修正後成績
- 努力程度比例

其中三科成績會使用 `Scores` 類來管理。

---

# 一、資料結構

建立一個 `Student` 物件後，資料結構如下：
```mermaid
Student
├─ id
├─ name
├─ scores (Scores)
│  ├─ chinese
│  ├─ english
│  └─ math
├─ effort_ratio
└─ fixed_score (Scores)
```
`scores`
-> 存放 **原始成績**

`fixed_score`
→ 存放 **修正後成績**

# 二、初始化 (`__init__`)

```python
def __init__(
    self,
    id_: str,
    name: str,
    chinese: Optional[float],
    english: Optional[float],
    math: Optional[float],
    *,
    effort_ratio: float = 0.5,
)
```
建立學生時需要：
| **參數** | **說明** |
| :--- | :--- |
| id_ | 學生ID |
| name | 學生姓名 |
| chinese | 國文成績 |
| english | 英文成績 |
| math | 數學成績 |
| effort_ratio | 努力程度比例 |

其中：
```python
None = 缺考
```
例如：
```python
student = Student("A01","Tom",90,80,None)
```
資料會變成：
```mermaid
Student
├─ id = A01
├─ name = Tom
├─ scores
│   ├─ chinese = 90
│   ├─ english = 80
│   └─ math = None
└─ effort_ratio = 0.5
```

# 三、CSV 轉換 Student (`parse_student`)
```python
@classmethod
def parse_student(cls, line: str)
```
這個方法用來 **把 CSV 一行資料轉換成 Student 物件**

CSV 格式：
```mermaid
id,name,chinese,english,math
```

例如：

> A01,Tom,90,80,

### 解析流程
```mermaid
CSV字串
   │
   ▼
split(",")
   │
   ▼
["A01","Tom","90","80",""]
   │
   ▼
解析三科分數
[90.0, 80.0, None]
   │
   ▼
建立 Student 物件
```

最後等同於：
```python
Student("A01","Tom",90,80,None)
```

# 四、計算修正分數 (`compute_fixed_score`)
如果某科缺考 (`None`)，就會計算補分

補分公式：
```mermaid
最低分 + (平均分 - 最低分) × effort_ratio
```

```python
def compute_fixed_score(self, avg_scores, min_scores)
```

計算依據：
* 班級平均分
* 班級最低分
* 學生努力比例

## 努力比例 (`effort_ratio`)
| **ratio** | **結果** |
| :--- | :--- |
| 1.0 | 平均分 |
| 0.5 | 平均與最低中間 |
| 0.0 | 最低分 |
| >1 | 超過平均 |
| <0 | 低於最低 |

## 計算流程
```mermaid
遍歷三科
   │
   ▼
取得原始分數
   │
   ├─ 有分數 → 直接使用
   │
   └─ 缺考
        │
        ▼
  使用公式計算修正分
        │
        ▼
加入 fixed_vals
        │
        ▼
建立 fixed_score
```

# 五、`fixed_total_score`
```python
@property
def fixed_total_score(self)
```
> 取得 **修正後總分**

# 六、`fixed_average`
```python
@property
def fixed_average(self)
```
> 取得 **修正後平均分**

# 七、完整流程
```mermaid
CSV資料
   │
   ▼
parse_student()
   │
   ▼
建立 Student
   │
   ▼
compute_fixed_score()
   │
   ▼
計算修正分
   │
   ▼
fixed_total_score
fixed_average
```

# 八、總結
`Student` 類負責：
* 儲存學生基本資料

* 管理三科成績

* 解析 CSV 資料

* 計算缺考科目的修正分數

* 提供修正後總分與平均
> 並透過 `Scores` 類來管理成績，使程式結構更清晰