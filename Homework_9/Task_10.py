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
    """Генерирует уникальный ID для задачи."""
    # Используем UUID4, чтобы гарантировать уникальность
    return str(uuid.uuid4())

class TaskHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        """Обработка GET /tasks — возврат списка всех задач."""
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/tasks':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(tasks).encode('utf-8'))
        else:
            self.send_error(404, "Не найден")

    def do_POST(self):
        """Обработка POST /tasks и POST /tasks/id/complete."""
        parsed_path = urlparse(self.path)

        # Создание новой задачи: POST /tasks
        if parsed_path.path == '/tasks':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))

                title = data.get('title')
                priority = data.get('priority')

                if not title or not priority:
                    self.send_error(400, "Поля 'title' и 'priority' обязательны")
                    return

                # Создаём новую задачу
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

        # Отметка о выполнении: POST /tasks/id/complete
        elif parsed_path.path.startswith('/tasks/') and parsed_path.path.endswith('/complete'):
            try:
                # Извлекаем ID из пути
                path_parts = parsed_path.path.strip('/').split('/')
                if len(path_parts) != 3 or path_parts[2] != 'complete':
                    self.send_error(400, "Неверный формат пути")
                    return

                task_id = path_parts[1]
                task = find_task(task_id)

                if task is None:
                    self.send_error(404, "Задача не найдена")
                    return

                task['isDone'] = True
                save_tasks()  # Сохраняем в файл

                self.send_response(200)
                self.end_headers()

            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404, "Не найден")

def run(server_class=HTTPServer, handler_class=TaskHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Сервер запущен на порту {port}...")
    load_tasks()  # Загружаем задачи при старте
    httpd.serve_forever()

if __name__ == '__main__':
    run()