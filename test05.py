from project import Student, calc_average, class_data, get_data

chin = 0
eng = 0
math = 0





for student in class_data.students:
    # print(student.name)
    # print(student.fixed_score.chinese_score)
    chin += student.fixed_score.chinese_score
    # print(student.fixed_score.english_score)
    eng += student.fixed_score.english_score
    # print(student.fixed_score.math_score)
    math += student.fixed_score.math_score


print(f"{chin:.2f} {eng:.2f} {math:.2f}")


c = calc_average(class_data.students, lambda x: x.fixed_score.chinese_score)
e = calc_average(class_data.students, lambda x: x.fixed_score.english_score)
m = calc_average(class_data.students, lambda x: x.fixed_score.math_score)
print(f'{c} {e} {m}')
