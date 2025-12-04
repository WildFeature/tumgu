word = input("Введите слово из латинских букв: ")  # Получаем слово от пользователя

if len(word) % 2 == 1:  # Проверяем, нечётное ли количество букв
    # Если нечётное — выводим среднюю букву
    middle_letter = word[len(word) // 2]
    print("Результат:", middle_letter)
else:  # Если чётное количество букв
    # Выводим две средние буквы
    middle_letters = word[len(word) // 2 - 1: len(word) // 2 + 1]
    print("Результат:", middle_letters)
