from .core import ClassData, Student


def get_data() -> list[Student]:
    data: list[Student] = []
    with open("data/student_scores_100_missing.csv", encoding="utf-8") as f:
        next(f)
        for line in f:
            data.append(Student.parse_student(line))
    return data

class_data = ClassData(get_data())
student_data: list[Student] = class_data.students
