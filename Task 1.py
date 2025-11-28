def is_leap_year(year):
    try:
        year = int(year)
    except ValueError:
        raise Exception("Требуется числовое значение")
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        return "Високосный год"
    else:
        return "Обычный год"

# Ввод года с клавиатуры
try:
    user_input = input("Введите год: ")
    result = is_leap_year(user_input)
    print(result)
except Exception as e:
    print(f"Ошибка: {e}")