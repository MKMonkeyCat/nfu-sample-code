from typing import (
    Callable,
    Generic,
    Iterable,
    List,
    Literal,
    Optional,
    Sequence,
    TypeVar,
)

_T = TypeVar("_T", float, Optional[float])
SubjectName = Literal["chinese", "english", "math"]

# 固定分數的最大增量，避免過度修正導致不合理的分數
FIXED_SCORE_SPACE = 10


class Scores(Generic[_T]):
    """一個簡單的類別來封裝學生的三科成績，提供一些方便的操作方法"""

    # 定義科目名稱的常量
    SUBJECTS: Sequence[SubjectName] = ("chinese", "english", "math")

    def __init__(self, chinese: _T, english: _T, math: _T) -> None:
        """初始化 Scores 物件，接受三科成績作為參數，可以是 float 或 None (表示缺考)"""
        self.chinese = chinese
        self.english = english
        self.math = math

    def get_by_name(self, name: SubjectName) -> _T:
        """根據科目名稱返回對應的成績值，如果名稱無效則拋出 ValueError"""
        if name not in self.SUBJECTS:
            raise ValueError(f"Invalid subject name: {name}")
        return getattr(self, name)

    @classmethod
    def from_iterable(cls, values: Iterable[_T]) -> "Scores":
        """從一個可迭代物件創建 Scores 物件，期望該物件包含三個元素，分別對應三科成績"""
        return cls(*values)

    def to_list(self) -> List[_T]:
        """將 Scores 物件的成績值以列表形式返回，順序為 [chinese, english, math]"""
        return [self.chinese, self.english, self.math]

    def __repr__(self) -> str:
        """提供 Scores 物件的字串表示，方便在調試和輸出時查看成績內容"""
        return f"Scores(Chi={self.chinese}, Eng={self.english}, Mat={self.math})"


class Student:
    def __init__(
        self,
        id_: str,
        name: str,
        chinese: Optional[float],
        english: Optional[float],
        math: Optional[float],
        *,
        effort_ratio: float = 0.5,
    ) -> None:
        """
        初始化 Student 物件，接受學生的 ID、姓名、三科成績以及努力程度比例 (effort_ratio)，
        努力程度比例用於計算修正後分數，默認為 0.5，表示介於平均分和最低分之間
        """
        self.id = id_
        self.name = name
        self.scores = Scores(chinese, english, math)
        self.effort_ratio = effort_ratio

        # fixed_score 屬性用於存儲計算後的修正分數，初始值為 None，表示尚未計算
        # 在 compute_fixed_score 方法中會根據原始分數、平均分、最低分和努力程度來計算修正分數，並將結果存儲在這個屬性中
        self.fixed_score: Scores[float]

    @classmethod
    def parse_student(cls, line: str) -> "Student":
        """解析 CSV 格式字串"""
        # CSV 的格式為: id, name, chinese, english, math，其中分數部分可能為空表示缺考
        parts = line.strip().split(",")
        # CSV 的前兩欄分別是學生 ID 和姓名
        id_, name = parts[0], parts[1]

        # 定義一個內部函數來解析分數，將空字串轉換為 None，非空字串轉換為 float ( 防止抱錯 )
        def _parse(s: str) -> Optional[float]:
            s = s.strip()
            return float(s) if s else None

        # CSV 的後三欄分別是三科成績，使用 _parse 函數來處理每個分數，得到一個包含三科成績的列表
        scores = map(_parse, parts[2:])
        # cls 是 Student 類別本身
        # 使用從 CSV 解析出的 ID、姓名和三科成績來創建一個 Student 物件並返回 (def __init__(...))
        return cls(id_, name, *scores)

    def compute_fixed_score(self, avg_scores: Scores[float], min_scores: Scores[float]) -> None:
        """
        根據學生的原始分數、班級的平均分、最低分和學生的努力程度來計算修正後的分數，並將結果存儲在 fixed_score 屬性中
        """
        fixed_vals: List[float] = []
        for sub in Scores.SUBJECTS:
            raw = self.scores.get_by_name(sub)
            if raw is not None:
                fixed_vals.append(raw)
                continue

            avg_v = avg_scores.get_by_name(sub)
            min_v = min_scores.get_by_name(sub)

            # effort_ratio:
            #   1.0 -> 平均分
            #   0.0 -> 最低分
            #   0.5 -> (平均 + 最低) / 2
            #   > 1.0 -> 超過平均分，根據比例增加
            #   < 0.0 -> 低於最低分，根據比例減少
            val = min_v + (avg_v - min_v) * self.effort_ratio
            # 不能超過 (平均分 + FIXED_SCORE_SPACE || 100)
            fixed_vals.append(min(max(val, 0), avg_v + FIXED_SCORE_SPACE, 100))

        self.fixed_score = Scores.from_iterable(fixed_vals)

        @property
        def fixed_total_score(self) -> float:
            """取得學生的修正後總分"""
            return sum(self.fixed_score.to_list())
        
        @property
        def fixed_average(self) -> float:
            """取得學生修正後平均"""
            vals = self.fixed_score.to_list()
            return sum(vals) / len(vals)

class ClassData:
    def __init__(self, students: List[Student]) -> None:
        """
        初始化 ClassData 物件，接受一個學生列表，並計算班級的統計數據 (平均分、最高分、最低分等)
        同時對每個學生應用分數修正邏輯來計算修正後的分數
        """
        # 學生列表，包含班級中所有學生的資料，每個學生都是一個 Student 物件，包含學生的 ID、姓名、原始分數、努力程度等資訊
        self.students = students

        # 原始分數的統計數據，包含平均分、最高分、最低分等資訊，這些數據是根據學生的原始分數計算得出的
        self.raw_avg_scores = self._generate_stat_scores(self._calc_average)
        # 最高分和最低分的計算邏輯類似，使用 max 和 min 函數來獲取每科的最高分和最低分，這些數據將用於後續的分數修正計算
        self.max_scores = self._generate_stat_scores(max)
        # 最低分的計算邏輯類似，使用 min 函數來獲取每科的最低分，這些數據將用於後續的分數修正計算
        self.min_scores = self._generate_stat_scores(min)

        # 自動對每個學生應用分數修正邏輯來計算修正後的分數
        # 這樣在後續的報表生成和分組邏輯中就可以直接使用修正後的分數來進行操作，而不需要每次都重新計算
        self._apply_score_fixing()

        # 修正後分數的統計數據，包含平均分、最高分、最低分等資訊，這些數據是根據學生的修正後分數計算得出的，將用於報表生成和分組邏輯等功能
        self.fixed_avg_scores = self._generate_fixed_stat_scores(self._calc_average)
        # 最高分和最低分的計算邏輯類似，使用 max 和 min 函數來獲取每科的修正後最高分和最低分，這些數據將用於報表生成和分組邏輯等功能
        self.fixed_max_scores = self._generate_fixed_stat_scores(max)
        # 最低分的計算邏輯類似，使用 min 函數來獲取每科的修正後最低分，這些數據將用於報表生成和分組邏輯等功能
        self.fixed_min_scores = self._generate_fixed_stat_scores(min)

    def _generate_stat_scores(self, stat_func: Callable[[Sequence[float]], float]) -> Scores[float]:
        """
        根據提供的統計函數 (例如平均分、最高分、最低分等) 來生成每科的統計數據，返回一個 Scores 物件，其中包含每科的統計結果
        """
        results: List[float] = []
        for sub in Scores.SUBJECTS:  # 依次處理科目
            valid_values: List[float] = [
                # 獲取該科目的所有有效成績 (即非 None 的成績)，這些成績將用於計算統計數據，例如平均分、最高分、最低分等
                v
                for s in self.students
                if (v := s.scores.get_by_name(sub)) is not None
            ]
            # 將實際有效成績傳給自訂函數
            # 如 stat_func = max 會取出該科最高成績
            results.append(stat_func(valid_values) if valid_values else 0)
        return Scores.from_iterable(results)

    def _generate_fixed_stat_scores(self, stat_func: Callable[[Sequence[float]], float]) -> Scores[float]:
        """
        根據提供的統計函數 (例如平均分、最高分、最低分等) 來生成每科的修正後統計數據，返回一個 Scores 物件，其中包含每科的統計結果
        """
        results: List[float] = []
        # 與上方的 _generate_stat_scores 類似
        # 不過這裡是基於學生的修正後分數 (fixed_score) 來計算統計數據
        for sub in Scores.SUBJECTS:
            all_values = [s.fixed_score.get_by_name(sub) for s in self.students]
            results.append(stat_func(all_values))
        return Scores.from_iterable(results)

    # 這個裝飾氣表示這個方法是靜態方法，不依賴於 ClassData 的實例
    # 可以直接通過類別名稱來調用，這裡用於計算平均分數的邏輯
    @staticmethod
    def _calc_average(data: Sequence[float]) -> float:
        return sum(data) / len(data)

    def _apply_score_fixing(self) -> None:
        """對每個學生應用分數修正邏輯來計算修正後的分數，並將結果存儲在學生的 fixed_score 屬性中"""
        # 對每個學生調用 compute_fixed_score 方法
        # 傳入班級的平均分和最低分，讓學生根據自己的努力程度來計算修正後的分數
        # 這樣在後續的報表生成和分組邏輯中就可以直接使用修正後的分數來進行操作，而不需要每次都重新計算
        for student in self.students:
            student.compute_fixed_score(self.raw_avg_scores, self.min_scores)

    # 這個裝飾器表示這個方法是類方法 (classmethod)，第一個參數是類別本身 (cls)，而不是實例
    # 可以通過類別名稱來調用，這裡用於從 CSV 文件中讀取學生資料並創建 ClassData 物件的邏輯
    @classmethod
    def from_file(cls, path: str) -> "ClassData":
        """從 CSV 文件中讀取學生資料並創建 ClassData 物件"""
        data: list[Student] = []
        with open(path, encoding="utf-8") as f:
            next(f)  # 跳過 CSV 的標題行
            for line in f:  # 逐行讀取
                # 使用 Student.parse_student 方法來解析每行的 CSV 字串
                # 解析後的 Student 物件會被添加到 data 列表中
                data.append(Student.parse_student(line))
        # 從剛剛抓到的學生資料列表來創建一個 ClassData 物件並返回
        # 這裡的 cls 就是 ClassData 類別本身
        return cls(data)
