def is_lucky_number(number):
    number = str(number)
    if len(number) != 6:
        return "Число должно быть длиной в 6 символов"
    if not number.isdigit():
        raise Exception("Требуется числовое значение")
    first_half_sum = sum(int(n) for n in number[:3])
    second_half_sum = sum(int(n) for n in number[3:6])
    if first_half_sum == second_half_sum:
        return "Счастливый билет"
    else:
        return "Несчастливый билет"

try:
    user_input = input("Введите шестизначный номер билета: ")
    result = is_lucky_number(user_input)
    print(result)
except Exception as e:
    print(f"Ошибка: {e}")
