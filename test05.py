from project import global_class_data

chin = 0
eng = 0
math = 0

print("學科平均分數：")
print(f"國文：{global_class_data.fixed_avg_scores.chinese:.2f}")
print(f"英文：{global_class_data.fixed_avg_scores.english:.2f}")
print(f"數學：{global_class_data.fixed_avg_scores.math:.2f}")
