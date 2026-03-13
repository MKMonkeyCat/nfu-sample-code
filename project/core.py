from typing import Callable, Iterable, TypeVar

_T = TypeVar("_T", float, None)
_Any = TypeVar("_Any")

def safe_parse_score(text: str) -> float | None:
    """將輸入的文字轉換為浮點數，如果輸入為空字串則返回 None。"""
    text = text.strip()
    if text == "":
        return None
    return float(text)

def calc_average(data: Iterable[_Any], func: Callable[[_Any], float | None]) -> float:
    """計算給定資料中，通過 func 提取的分數的平均值，忽略 None 值。"""
    total, valid_count = 0, 0
    for item in data:
        score = func(item)
        if score is not None:
            total += score
            valid_count += 1

    return 0 if valid_count == 0 else total / valid_count



class Scores[T]:
    """Scores 類別用於表示學生的三科成績，類型可以是浮點數或 None"""
    def __init__(self, chinese_score: T, english_score: T, math_score: T) -> None:
        self.chinese_score = chinese_score
        self.english_score = english_score
        self.math_score = math_score

class ClassData:
    # 學生物件定義
    def __init__(self, students: list["Student"]) -> None:
        self.students = students

        # 計算跳過空值得全班平均分數，並用於填補缺失分數
        self.fail_default_scores = Scores(
            calc_average(self.students, lambda student: student.scores.chinese_score),
            calc_average(self.students, lambda student: student.scores.english_score),
            calc_average(self.students, lambda student: student.scores.math_score),
        )

        # 計算各科最高成績，用於限制填補分數的上限，避免出現不合理的分數
        self.max_scores = Scores(
            max(student.scores.chinese_score for student in self.students if student.scores.chinese_score is not None),
            max(student.scores.english_score for student in self.students if student.scores.english_score is not None),
            max(student.scores.math_score for student in self.students if student.scores.math_score is not None),
        )

        # 填補缺失分數並生成新的學生列表
        for student in students:
            scores = student.scores

            def d(score: float | None, default: float, max_value: float) -> float:
                return min(score if score is not None else default, max_value)
            
            student.fixed_score = Scores(
                d(scores.chinese_score, self.fail_default_scores.chinese_score, self.max_scores.chinese_score),
                d(scores.english_score, self.fail_default_scores.english_score, self.max_scores.english_score),
                d(scores.math_score, self.fail_default_scores.math_score, self.max_scores.math_score),
            )

        # 計算填補後的全班平均分數
        self.fixed_average_scores = Scores(
            calc_average(self.students, lambda student: student.fixed_score.chinese_score),
            calc_average(self.students, lambda student: student.fixed_score.english_score),
            calc_average(self.students, lambda student: student.fixed_score.math_score),
        )

# 學生物件定義
class Student:
    """
    Student 類別用於表示學生的基本資訊和成績。
    屬性:
    - id: 學生的唯一識別碼 (字串)
    - name: 學生的姓名 (字串)
    - chinese_score: 學生的國文成績 (浮點數或 None)
    - english_score: 學生的英文成績 (浮點數或 None)
    - math_score: 學生的數學成績 (浮點數或 None)
    """
    def __init__(
        self,
        id_: str,
        name: str,
        chinese_score: float | None,
        english_score: float | None,
        math_score: float | None,
    ) -> None:
        self.id = id_
        self.name = name
        self.scores = Scores(chinese_score, english_score, math_score)
        self.fixed_score: Scores[float]  # 將在 ClassData 中填補缺失分數後賦值

    def __str__(self) -> str:
        """定義 Student 物件的字串表示方式，方便打印學生資訊"""
        scores = self.scores
        return f"{self.name} (ID: {self.id}) - Chinese: {scores.chinese_score}, English: {scores.english_score}, Math: {scores.math_score}"

    @classmethod
    def parse_student(cls, line: str) -> "Student":
        id_, name, *scores = line.strip().split(",")
        return cls(id_, name, *map(safe_parse_score, scores))
