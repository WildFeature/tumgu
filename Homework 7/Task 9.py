import csv
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('validation_errors.log', encoding='utf-8'),
        logging.StreamHandler()  # вывод в консоль
    ]
)

def load_csv_data(filename):
    """Загружает данные из CSV-файла с заголовками."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
    except FileNotFoundError:
        logging.error(f"Файл {filename} не найден.")
        return []
    except Exception as e:
        logging.error(f"Ошибка при чтении файла {filename}: {e}")
        return []

def parse_field(value):
    """Очищает значение поля от лишних пробелов."""
    return value.strip() if value else ''

def is_valid_age(age_str):
    """Проверяет, что возраст — целое число в диапазоне 1 < age <= 100."""
    age_str = parse_field(age_str)
    if not age_str.isdigit():
        return False
    age = int(age_str)
    return 0 < age <= 100

def is_valid_sex(sex_str):
    """Проверяет, что пол — 'male' или 'female'."""
    sex = parse_field(sex_str).lower()
    return sex in ('male', 'female')

def is_valid_bill(bill_str):
    """Проверяет, что bill — положительное число (целое или дробное)."""
    bill_str = parse_field(bill_str)
    try:
        bill = float(bill_str)
        return bill > 0
    except ValueError:
        return False

def format_age(age_str):
    """Форматирует возраст (добавляет 'лет')."""
    age = parse_field(age_str)
    return f"{age} лет"

def format_gender(gender_str):
    """Преобразует пол в текстовое описание."""
    gender = parse_field(gender_str).lower()
    if gender == 'female':
        return 'женского пола'
    elif gender == 'male':
        return 'мужского пола'
    else:
        return gender  # на случай, если валидация пропущена

def format_device(device_str):
    """Преобразует устройство в читаемый формат."""
    device = parse_field(device_str).lower()
    if 'mobile' in device:
        return 'мобильного'
    elif 'desktop' in device:
        return 'стационарного'
    else:
        return device

def format_amount(amount_str):
    """Форматирует сумму чека."""
    amount = parse_field(amount_str)
    return f"{amount} у.е."

def create_description(row):
    """
    Описание покупателя на основе данных строки.
    """
    # Извлекаем и очищаем поля
    name = parse_field(row.get('name', ''))
    sex = parse_field(row.get('sex', ''))
    age = parse_field(row.get('age', ''))
    device_type = parse_field(row.get('device_type', ''))
    browser = parse_field(row.get('browser', ''))
    bill = parse_field(row.get('bill', ''))
    region = parse_field(row.get('region', ''))  # не проверяем на пустоту

    # Валидация обязательных полей
    if not name:
        logging.warning("Пропущено: пустое поле 'name'.")
        return None
    if not is_valid_sex(sex):
        logging.warning(f"Пропущено: некорректный пол '{sex}' для имени {name}.")
        return None
    if not is_valid_age(age):
        logging.warning(f"Пропущено: некорректный возраст '{age}' для имени {name}.")
        return None
    if not is_valid_bill(bill):
        logging.warning(f"Пропущено: некорректная сумма чека '{bill}' для имени {name}.")
        return None

    # Форматируем данные
    gender = format_gender(sex)
    age_formatted = format_age(age)
    device = format_device(device_type)
    amount = format_amount(bill)

    # Согласование глагола по полу
    verb = "совершил" if sex == "male" else "совершила"

    return (f"Пользователь {name} {gender}, {age_formatted} {verb} покупку на {amount} "
            f"с {device} браузера {browser}. Регион, из которого совершалась покупка: {region}.")

def save_descriptions_to_file(descriptions, output_filename):
    """Сохраняет описания в текстовый файл."""
    with open(output_filename, 'w', encoding='utf-8') as file:
        for desc in descriptions:
            if desc:  # пропускаем None
                file.write(desc + '\n')

def process_data(input_filename, output_filename):
    """Основная функция обработки данных."""
    # Шаг 1: Загрузка данных
    data = load_csv_data(input_filename)
    if not data:
        logging.error("Нет данных для обработки.")
        return

    # Шаг 2–3: Парсинг и преобразование данных
    descriptions = []
    for i, row in enumerate(data, 1):
        # Шаг 4: Формирование описания
        description = create_description(row)
        if description:
            descriptions.append(description)
        else:
            logging.info(f"Строка {i} пропущена из-за ошибок валидации.")

    # Шаг 5: Запись в файл
    if descriptions:
        save_descriptions_to_file(descriptions, output_filename)
        logging.info(f"Обработано {len(descriptions)} корректных записей. Результат записан в {output_filename}.")
    else:
        logging.warning("Ни одна запись не прошла валидацию. Выходной файл не создан.")

# Запуск обработки
if __name__ == '__main__':
    process_data('web_clients_correct.csv', 'descriptions.txt')
