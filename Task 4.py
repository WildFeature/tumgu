# Исходные списки юношей и девушек
boys = ['Peter', 'Alex', 'John', 'Arthur', 'Richard', 'Michael']
girls = ['Kate', 'Liza', 'Kira', 'Emma', 'Trisha']

# Сортируем списки по алфавиту
boys_sorted = sorted(boys)
girls_sorted = sorted(girls)

# Проверяем, равны ли длины списков (чтобы никто не остался без пары)
if len(boys_sorted) == len(girls_sorted):
    print("Идеальные пары:")
    # Создаём пары, сопоставляя элементы с одинаковыми индексами
    for i in range(len(boys_sorted)):
        print(f"{boys_sorted[i]} и {girls_sorted[i]}")
else:
    print("Внимание, кто-то может остаться без пары.")
