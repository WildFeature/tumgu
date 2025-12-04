from datetime import datetime
# Исходные строки с названиями газет и датами
input_strings = [
    "The Moscow Times — Wednesday, October 2, 2002",
    "The Guardian — Friday, 11.10.13",
    "Daily News — Thursday, 18 August 1977"
]
# Словарь с форматами для каждой газеты
date_formats = {
    "The Moscow Times": "%A, %B %d, %Y",
    "The Guardian": "%A, %d.%m.%y",
    "Daily News": "%A, %d %B %Y"
}
# Проходим по каждой строке
for string in input_strings:
    newspaper, date_str = string.split(" — ")
    format_str = date_formats[newspaper]
    dt = datetime.strptime(date_str, format_str)
    print(f"{newspaper}: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
