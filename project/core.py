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
    SUBJECTS: Sequence[SubjectName] = ("chinese", "english", "math")

    def __init__(self, chinese: _T, english: _T, math: _T) -> None:
        self.chinese = chinese
        self.english = english
        self.math = math

    def get_by_name(self, name: SubjectName) -> _T:
        if name not in self.SUBJECTS:
            raise ValueError(f"Invalid subject name: {name}")
        return getattr(self, name)

    @classmethod
    def from_iterable(cls, values: Iterable[_T]) -> "Scores":
        return cls(*values)

    def to_list(self) -> List[_T]:
        return [self.chinese, self.english, self.math]

    def __repr__(self) -> str:
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
        self.id = id_
        self.name = name
        self.scores = Scores(chinese, english, math)
        self.effort_ratio = effort_ratio

        self.fixed_score: Scores[float]

    @classmethod
    def parse_student(cls, line: str) -> "Student":
        """解析 CSV 格式字串"""
        parts = line.strip().split(",")
        id_, name = parts[0], parts[1]

        def _parse(s: str) -> Optional[float]:
            s = s.strip()
            return float(s) if s else None

        scores = map(_parse, parts[2:])
        return cls(id_, name, *scores)

    def compute_fixed_score(self, avg_scores: Scores[float], min_scores: Scores[float]) -> None:
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


class ClassData:
    def __init__(self, students: List[Student]) -> None:
        self.students = students

        self.raw_avg_scores = self._generate_stat_scores(self._calc_average)
        self.max_scores = self._generate_stat_scores(lambda data: max(data) if data else 0)
        self.min_scores = self._generate_stat_scores(lambda data: min(data) if data else 0)

        self._apply_score_fixing()

        self.fixed_avg_scores = self._generate_fixed_stat_scores(self._calc_average)

    def _generate_stat_scores(self, stat_func: Callable[[Sequence[float]], float]) -> Scores[float]:
        results: List[float] = []
        for sub in Scores.SUBJECTS:
            valid_values: List[float] = [
                v for s in self.students if (v := s.scores.get_by_name(sub)) is not None
            ]
            results.append(stat_func(valid_values) if valid_values else 0)
        return Scores.from_iterable(results)

    def _generate_fixed_stat_scores(self, stat_func: Callable[[Sequence[float]], float]) -> Scores[float]:
        results: List[float] = []
        for sub in Scores.SUBJECTS:
            all_values: List[float] = [s.fixed_score.get_by_name(sub) for s in self.students]
            results.append(stat_func(all_values))
        return Scores.from_iterable(results)

    @staticmethod
    def _calc_average(data: Sequence[float]) -> float:
        return sum(data) / len(data) if data else 0

    def _apply_score_fixing(self) -> None:
        for student in self.students:
            student.compute_fixed_score(self.raw_avg_scores, self.min_scores)
