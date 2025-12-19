import requests
from flask import Flask, render_template_string
import sys
import os

app = Flask(__name__)

# 1. БЕЗОПАСНОСТЬ: Ввод токена ОДИН РАЗ при старте системы.
# Ключ не хранится в коде, чтобы избежать его попадания в публичный репозиторий.
print("=" * 50)
print("ЗАПУСК СЕРВЕРА (Яндекс Диск API v1)")
print("=" * 50)
GLOBAL_TOKEN = input("Введите ваш OAuth-токен Яндекс Диска: ").strip()

if not GLOBAL_TOKEN:
    print("Ошибка: токен не может быть пустым!")
    sys.exit(1)

def get_yandex_files(token):
    """
    Получает список файлов из корня Яндекс Диска через API.
    Используется документация: yandex.ru
    """
    headers = {'Authorization': f'OAuth {token}'}
    # ИСПРАВЛЕНО: Полный URL с протоколом https и корректным путем к ресурсам
    url = 'cloud-api.yandex.net'
    params = {'path': '/', 'limit': 100}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Документация говорит, что список ресурсов лежит в ключе _embedded
            items = data.get('_embedded', {}).get('items', [])
            return [item['name'] for item in items if item['type'] == 'file']
        else:
            print(f"Ошибка API: {response.status_code}")
            return []
    except Exception as e:
        print(f"Ошибка соединения: {e}")
        return []

@app.route('/')
def index():
    # Получаем актуальный список имен файлов с облака
    uploaded_on_disk = get_yandex_files(GLOBAL_TOKEN)

    # Получаем список всех файлов в текущей локальной папке проекта
    my_files = [f for f in os.listdir('.') if os.path.isfile(f)]

    # HTML-шаблон со встроенными стилями
    html_template = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Файлы проекта</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f8f9fa; }
            h1 { color: #2c3e50; }
            ul { padding: 0; }
            li {
                padding: 15px;
                margin: 10px 0;
                list-style: none;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
            }
            /* КРИТЕРИЙ ЗАДАНИЯ: Фоновый цвет rgba(0, 200, 0, 0.25) */
            .uploaded { 
                background-color: rgba(0, 200, 0, 0.25); 
                border-color: #2ecc71;
            }
            .status { float: right; color: #27ae60; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Список файлов сервера</h1>
        <p>Подсвечены файлы, которые уже есть на вашем Яндекс Диске.</p>
        <ul>
        {% for file in files %}
            <li class="{{ 'uploaded' if file in uploaded else '' }}">
                <span>{{ file }}</span>
                {% if file in uploaded %}
                    <span class="status">✓ Загружено на Диск</span>
                {% endif %}
            </li>
        {% endfor %}
        </ul>
    </body>
    </html>
    """

    return render_template_string(
        html_template,
        files=my_files,
        uploaded=uploaded_on_disk
    )

if __name__ == '__main__':
    # В 2025 году Flask по умолчанию работает на порту 5000
    print(f"Сервер запускается... Откройте http://127.0.0.1:5000")
    # debug=False предотвращает сбои при вводе данных в терминал PyCharm
    app.run(host='127.0.0.1', port=5000, debug=False)