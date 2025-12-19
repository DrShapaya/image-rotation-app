# README

Веб-приложение для поворота изображений

## Возможности
Загрузка изображений формата JPEG/PNG
- Поворот изображения на произвольный угол
- Генерация **гистограммы цветов** исходного изображения
- Проверка CAPTCHA для предотвращения автоматических загрузок
- Вывод повернутого изображения и гистограммы прямо на странице

##  Технологии

- **Backend:** FastAPI, Python
- **Frontend:** HTML, Jinja2, Bootstrap Superhero
- **Обработка изображений:** Pillow, NumPy, Matplotlib
- **Безопасность:** reCAPTCHA
- **Деплой:** Uvicorn

##  Установка и запуск

```bash
# Клонировать репозиторий
git clone git@github.com:DrShapaya/image-rotation-app.git
cd image-rotation-app

# Установить зависимости
pip install -r requirements.txt

# Запустить сервер
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Версия пайтона
python-3.11.0

# Конфигурационные файлы
fastapi==0.104.1
uvicorn[standard]==0.24.0
pillow==10.1.0
numpy==1.24.3
matplotlib==3.8.2
python-multipart==0.0.6
jinja2==3.1.2
