import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import uuid

# Файл для хранения задач
TASKS_FILE = 'tasks.txt'

# Список задач (в памяти)
tasks = []


def load_tasks():
    """Загружает задачи из файла при старте сервера."""
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                data = f.read()
                if data.strip():
                    tasks.extend(json.loads(data))
        except (json.JSONDecodeError, IOError):
            print(f"Ошибка при чтении {TASKS_FILE}. Начинаем с пустого списка.")


def save_tasks():
    """Сохраняет текущий список задач в файл."""
    try:
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Ошибка при записи в {TASKS_FILE}: {e}")


def find_task(task_id):
    """Находит задачу по ID."""
    for task in tasks:
        if task['id'] == task_id:
            return task
    return None


def generate_id():
    """Генерирует уникальный числовой ID для задачи."""
    # Используем UUID4, преобразуем в число
    return int(uuid.uuid4().int >> 64)  # Сокращаем длину числа


class TaskHandler(BaseHTTPRequestHandler):

    def send_error(self, code, message=None):
        """Переопределённый send_error с поддержкой UTF-8."""
        if message is None:
            message = self.responses.get(code, ('???', '???'))[0]
        safe_message = message.encode('utf-8', 'replace').decode('latin-1', 'replace')
        self.send_response_only(code, safe_message)
        self.send_header('Connection', 'close')
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/tasks':
            self._handle_get_tasks()
        elif parsed_path.path == '/':
            self._handle_root()
        else:
            self.send_error(404, "Не найден")

    def _handle_root(self):
        """Обрабатывает запрос к корневой странице."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = json.dumps({
            "message": "API Задача-трекер",
            "endpoints": ["/tasks", "/tasks/{id}/complete"]
        })
        self.wfile.write(response.encode('utf-8'))

    def _handle_get_tasks(self):
        """Возвращает список всех задач."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(tasks).encode('utf-8'))

    def do_POST(self):
        """Обработка POST-запросов."""
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/tasks':
            self._handle_create_task()
        elif parsed_path.path.startswith('/tasks/') and parsed_path.path.endswith('/complete'):
            self._handle_complete_task(parsed_path)
        else:
            self.send_error(404, "Не найден")

    def _handle_create_task(self):
        """Создаёт новую задачу."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            title = data.get('title')
            priority = data.get('priority')

            if not title or not priority:
                self.send_error(400, "Поля 'title' и 'priority' обязательны")
                return

            # Создаём новую задачу с числовым ID
            task = {
                'id': generate_id(),
                'title': title,
                'priority': priority,
                'isDone': False
            }

            tasks.append(task)
            save_tasks()  # Сохраняем в файл

            self.send_response(201)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(task).encode('utf-8'))

        except json.JSONDecodeError:
            self.send_error(400, "Неверный JSON")
        except Exception as e:
            self.send_error(500, str(e))

    def _handle_complete_task(self, parsed_path):
        try:
            path_parts = parsed_path.path.strip('/').split('/')
            if len(path_parts) != 3 or path_parts[2] != 'complete':
                self.send_error(400, "Неверный формат пути")
                return

            # ПРЕОБРАЗОВАНИЕ: строка → число
            task_id = int(path_parts[1])  # вот здесь!

            task = find_task(task_id)
            if task is None:
                self.send_error(404, "Задача не найдена")
                return

            task['isDone'] = True
            save_tasks()
            self.send_response(200)
            self.end_headers()

        except Exception as e:
            self.send_error(500, str(e))


def run(server_class=HTTPServer, handler_class=TaskHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Сервер запущен на порту {port}...")
    load_tasks()  # Загружаем задачи при старте
    httpd.serve_forever()


if __name__ == '__main__':
    run()