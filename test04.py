class Student:
    def __init__(
            self,
            id_: str,
            name: str,
            chinese_score: float | None,    
            english_score: float | None,    
            math_score: float | None,):     
        
        self.id = id_
        self.name = name
        self.chinese_score = chinese_score
        self.english_score = english_score
        self.math_score = math_score

    def calculate_average(self):
        scores = [self.chinese_score, self.english_score, self.math_score]
        vaild_scores = [s for s in scores if s is not None]

        if len(vaild_scores) > 0:
            return sum(vaild_scores) / len(vaild_scores)
        return 0.0

    def __str__(self):
        return f"{self.name} (ID: {self.id}) - Chinese: {self.chinese_score}, English: {self.english_score}, Math: {self.math_score}"

def parse_score(text: str) -> float | None:
    text = text.strip()
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None

def main():
    data: list[Student] = []
    with open("data/student_scores_100_missing.csv", encoding="utf-8") as f:
        next(f)
        for line in f:
            id_, name, chinese_score, english_score, math_score = line.strip().split(",")
            data.append(Student(id_, name, parse_score(chinese_score), parse_score(english_score), parse_score(math_score)))

    print("## CSV 檔案讀取與資料解析")
    for student in data[:5]:
        print(str(student))

    print("## ")

    ranked_students = sorted(data, key = lambda x: x.calculate_average(), reverse=True)

    print("小組平均成績與排名")
    for rank, student in enumerate(ranked_students, 1):
        avg = student.calculate_average()
        print(f"第 {rank} 名: {student.name}, 平均分: {avg:.2f}")


if __name__ == "__main__":
    main()
