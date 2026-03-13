from project.core import ClassData


def step3(class_data: ClassData):
    fixed_avg_scores = class_data.fixed_average_scores
    print(f"{fixed_avg_scores.chinese_score:.2f} {fixed_avg_scores.english_score:.2f} {fixed_avg_scores.math_score:.2f}")

    print(max(class_data.students, key=lambda student: student.fixed_score.chinese_score).fixed_score.math_score)
    print(max(class_data.students, key=lambda student: student.fixed_score.english_score).fixed_score.math_score)
    print(max(class_data.students, key=lambda student: student.fixed_score.math_score).fixed_score.math_score)


if __name__ == "__main__":
    from project.data import class_data

    step3(class_data)
