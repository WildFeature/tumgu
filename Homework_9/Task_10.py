import json
import os
import http.server
import urllib.request
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Константы
PORT = 8000
DB_FILE = "tasks.txt"
# Для работы Vulners API нужен ключ. Если его нет, поиск будет ограничен или вернет ошибку.
VULNERS_API_KEY = "N459W3MF3LGXLGZBX4437RLRXWSEX7Y1L77LTDJCPFAU7WNTAQDX1PZ5PR5FCSE4"


class TaskManager:
    def __init__(self):
        self.tasks = []
        self.next_id = 1
        self.load_tasks()

    def load_tasks(self):
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = data
                    if self.tasks:
                        self.next_id = max(t['id'] for t in self.tasks) + 1
                logging.info(f"Загружено {len(self.tasks)} задач из {DB_FILE}")
            except (json.JSONDecodeError, TypeError, ValueError, IOError) as e:
                logging.error(f"Ошибка при чтении {DB_FILE}: {e}")
                self.tasks = []

    def save_tasks(self):
        try:
            with open(DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=4)
            logging.info(f"Задачи сохранены в {DB_FILE}")  # Исправлено: f-строка, нет лишнего пробела
        except IOError as e:
            logging.error(f"Ошибка записи в {DB_FILE}: {e}")  # Исправлено: f-строка
            raise

    def add_task(self, title, priority):
        """Создаёт новую задачу и проверяет уязвимости."""
        if priority not in ['low', 'normal', 'high']:
            raise ValueError("Приоритет должен быть low, normal или high")

        vulnerability_info = self.check_vulnerabilities(title)
        is_vulnerable = bool(vulnerability_info)

        task = {
            "id": int(self.next_id),
            "title": title,
            "priority": priority,
            "isDone": False,
            "vulnerability_found": vulnerability_info is not None
        }
        self.tasks.append(task)
        self.next_id += 1
        self.save_tasks()
        logging.info(f"Создана задача ID={task['id']}: {task['title']}")  # Исправлено: f-строка
        return task

    def complete_task(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                task['isDone'] = True
                self.save_tasks()
                logging.info(f"Задача ID={task_id} отмечена как выполненная")  # Исправлено: f-строка
                return True
        return False

    def check_vulnerabilities(self, software_name):
        if not VULNERS_API_KEY or VULNERS_API_KEY == "N459W3MF3LGXLGZBX4437RLRXWSEX7Y1L77LTDJCPFAU7WNTAQDX1PZ5PR5FCSE4":
            return None

        try:
            query = f'"software:{software_name}"'  # Добавлено: кавычки
            url = (f"https://vulners.com/api/v3/search/lucene/"
                   f"?query={query}&api_key={VULNERS_API_KEY}&size=1")

            with urllib.request.urlopen(url, timeout=5) as response:
                if response.getcode() != 200:
                    return None
                data = json.loads(response.read().decode())
                if data.get('result') == 'success' and data['data']['total'] > 0:
                    return data['data']['search'][0]['id']
        except Exception as e:
            logging.error(f"Ошибка при запросе к Vulners: {e}")  # print → logging
            return None
        return None


class TaskHandler(http.server.BaseHTTPRequestHandler):
    manager = TaskManager()

    def do_GET(self):
        if self.path == '/tasks':
            self.handle_get_tasks()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/tasks':
            self.handle_create_task()
        elif self.path.startswith('/tasks/') and self.path.endswith('/complete'):
            self.handle_complete_task()
        else:
            self.send_error(404)

    # Декомпозированные методы обработки

    def handle_get_tasks(self):
        response = json.dumps(self.manager.tasks)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))



    def handle_create_task(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_error(400, "Тело запроса пустое")
            return

        try:
            body = json.loads(self.rfile.read(content_length).decode('utf-8'))
            if 'title' not in body or 'priority' not in body:
                raise ValueError("Обязательны поля: title и priority")

            new_task = self.manager.add_task(body['title'], body['priority'])

            self.send_response(201)
            self.send_header('Content-Type', 'application/json')
            response = json.dumps(new_task)
            self.send_header('Content-Length', str(len(response)))
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
        except json.JSONDecodeError:
            self.send_error(400, "Неверный JSON")
        except ValueError as e:
            self.send_error(400, str(e))
        except Exception as e:
            logging.error(f"Ошибка при создании задачи: {e}")
            self.send_error(500, "Внутренняя ошибка сервера")

    def handle_complete_task(self):
        try:
            parts = self.path.strip('/').split('/')
            if len(parts) != 3 or parts[2] != 'complete':
                self.send_error(400, "Неверный формат URL")
                return

            try:
                task_id = int(parts[1])
                if task_id <= 0:
                    self.send_error(400, "ID должен быть положительным числом")
                    return
            except ValueError:
                self.send_error(400, "ID должен быть числом")
                return

            if self.manager.complete_task(task_id):
                self.send_response(200)
                self.end_headers()
            else:
                self.send_error(404, "Задача не найдена")
        except Exception as e:
            logging.error(f"Ошибка при обработке complete-запроса: {e}")  # Убран пробел и дефис
            self.send_error(500, "Внутренняя ошибка сервера")


if __name__ == '__main__':
    server = http.server.HTTPServer(('localhost', PORT), TaskHandler)
    print(f"Сервер запущен на http://localhost:{PORT}")
    server.serve_forever()