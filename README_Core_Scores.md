# Scores 類別說明

`Scores` 是一個用來 **封裝學生三科成績** 的類別。  
它把「國文、英文、數學」三個分數集中在一個物件中，並提供一些方便的方法來操作這些成績。

---

# 一、Scores 類的概念

當我們建立一個 `Scores` 物件時，資料結構會像這樣：

```python
Scores
├─ chinese
├─ english
└─ math
```


例如：

```python
scores = Scores(90, 80, 70)
```

物件內部會變成：
```python 
scores
├─ chinese = 90
├─ english = 80
└─ math = 70
```

這樣做的好處：

* **成績資料被集中管理**

* **程式結構更清楚**

* **更容易擴充功能**

# 二、初始化(__init__)
```python
def __init__(self, chinese, english, math):
    self.chinese = chinese
    self.english = english
    self.math = math
```
當建立 Scores 物件時，會自動執行 `__init__`
例如：
```python
scores = Scores(90, 80, 70)
```
執行流程：
```python
Scores(90,80,70)
      │
      ▼
__init__(self, 90,80,70)
      │
      ▼
self.chinese = 90
self.english = 80
self.math = 70
```

# 三、SUBJECTS（科目清單）
```python
SUBJECTS = ("chinese", "english", "math")
```
`SUBJECTS` 定義了一個 **合法科目名稱的清單** <br>
程式會透過檢查 `if subject not in SUBJECTS` 來確保輸入的科目名稱是有效的。
若輸入錯誤，會拋出 ValueError

例如：
```python
chinese ✔
english ✔
math ✔
history ✘
```

用途：
* **提供一個 可接受的科目名稱範圍**
* **讓程式可以檢查輸入是否正確**
* **避免使用不存在的科目名稱**

# 四、get_by_name()
```python
def get_by_name(self, name):
    if name not in self.SUBJECTS:
        raise ValueError("Invalid subject name")
    return getattr(self, name)
```
這個方法可以 **用科目名稱取得對應成績**
例如：
```python
scores = Scores(90,80,70)

scores.get_by_name("math")
```
回傳：
> 70

### 為什麼要用 getattr？
如果不用 `getattr`，程式可能會變成：

```python
if name == "chinese":
    return self.chinese
elif name == "english":
    return self.english
elif name == "math":
    return self.math
```

使用 `getattr` 可以簡化成：
```python
getattr(self, name)
```
意思是：
```python
取得 self.<name> 的屬性
```

例如：
```python
name = "math"

getattr(self, name)
→ self.math
```

# 五、from_iterable()
```python
@classmethod
def from_iterable(cls, values):
    return cls(*values)
```
**替代的建立方式**
通常建立 `Scores`：
```python
Scores(90,80,70)
```
但如果資料是 `list`：
```python
values = [90,80,70]
```
就可以寫：
```python
Scores.from_iterable(values)
```

### *values 的作用
如果：
```python
values = [90,80,70]
```
`*values` 會展開成：
```python
90,80,70
```
所以：
```python
cls(*values)
```
等於：
```python
Scores(90,80,70)
```
# 六、to_list()
可以把 `Scores` 物件轉換成 **list**
例如：
```python
scores = Scores(90,80,70)

scores.to_list()
```
結果：
```python
[90,80,70]
```
用途：
* **儲存資料**
* **輸出資料**
* **計算平均**

# 七、repr()
```python
def __repr__(self):
    return f"Scores(Chi={self.chinese}, Eng={self.english}, Mat={self.math})"
```
`__repr__` 用來 **定義物件被印出時的顯示方式**

例如：
```python
scores = Scores(90,80,70)

print(scores)
```
輸出：
```python
Scores(Chi=90, Eng=80, Mat=70)
```
如果沒有 `__repr__`，可能會顯示：
```python
<__main__.Scores object at 0x001F32A>
```
# 八、完整使用範例
```python
scores = Scores(90,80,70)

print(scores)

print(scores.get_by_name("english"))

print(scores.to_list())
```
輸出：
```python
Scores(Chi=90, Eng=80, Mat=70)
80
[90,80,70]
```

# 九、總結
`Scores` 類主要負責：

* **儲存三科成績**

* **透過科目名稱取得成績**

* **支援 list 建立物件**

* **能轉換成 list**

* **提供清楚的輸出格式**
