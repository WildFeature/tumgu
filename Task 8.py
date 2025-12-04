import json
import zipfile

# 1. Открываем ZIP-архив и читаем purchase_log.txt внутри него
pokupka_po_userId = {}
with zipfile.ZipFile('purchase_log.zip', 'r') as zip_file:
    with zip_file.open('purchase_log.txt') as fail_pokupok:
        for stroka in fail_pokupok:
            stroka = stroka.decode('utf-8').strip()  # декодируем байты в строку и убираем пробелы
            dannie = json.loads(stroka)
            pokupka_po_userId[dannie['user_id']] = dannie['category']

print(f"Загружено {len(pokupka_po_userId)} покупок")

# 2. Обработка visit_log.csv и запись funnel.csv (в одном блоке)
with open('visit_log__1_.csv', 'r', encoding='utf-8') as fail_vizitov, \
        open('funnel.csv', 'w', encoding='utf-8') as fail_voronka:
    # Записываем заголовок
    fail_voronka.write('user_id,source,category\n')

    # Пропускаем первую строку (заголовок) и обрабатываем остальные
    next(fail_vizitov)  # пропускаем заголовок

    for stroka_vizita in fail_vizitov:
        stroka_vizita = stroka_vizita.strip()
        if not stroka_vizita:  # защита от пустых строк
            continue

        user_id, source = stroka_vizita.split(',')

        # Если user_id есть в покупках — записываем строку
        if user_id in pokupka_po_userId:
            kategoriya = pokupka_po_userId[user_id]
            fail_voronka.write(f'{user_id},{source},{kategoriya}\n')

print("Готово! Файл funnel.csv создан")

# 3. Проверка первых строк результата
with open('funnel.csv', 'r', encoding='utf-8') as fail_result:
    for i, line in enumerate(fail_result, 1):
        if i <= 4:  # выводим только первые 4 строки
            print(line.strip())
        else:
            break
