# Исходные данные
documents = [
    {'type': 'passport', 'number': '2207 876234', 'name': 'Василий Гупкин'},
    {'type': 'invoice', 'number': '11-2', 'name': 'Геннадий Покемонов'},
    {'type': 'insurance', 'number': '10006', 'name': 'Аристарх Павлов'}
]

directories = {
    '1': ['2207 876234', '11-2'],
    '2': ['10006'],
    '3': []
}

# Функция для поиска владельца документа по номеру
def get_document_owner(doc_number):
    for doc in documents:
        if doc['number'] == doc_number:
            return doc['name']
    return None

# Функция для поиска полки, на которой хранится документ
def get_shelf_number(doc_number):
    for shelf, doc_list in directories.items():
        if doc_number in doc_list:
            return shelf
    return None

# Основная программа с циклом ввода команд
def main():
    print("Секретарский помощник. Введите команду (p — узнать владельца, s — узнать полку, q — выйти):")
    while True:
        command = input("\nВведите команду: ").strip().lower()
        if command == 'q':
            print("Программа завершена.")
            break
        elif command == 'p':
            doc_number = input("Введите номер документа: ").strip()
            owner = get_document_owner(doc_number)
            if owner:
                print(f"Владелец документа: {owner}")
            else:
                print("Документ не найден в базе.")
        elif command == 's':
            doc_number = input("Введите номер документа: ").strip()
            shelf = get_shelf_number(doc_number)
            if shelf:
                print(f"Документ хранится на полке: {shelf}")
            else:
                print("Документ не найден в базе.")
        else:
            print("Неизвестная команда. Используйте p, s или q.")

# Запуск программы
if __name__ == '__main__':
    main()