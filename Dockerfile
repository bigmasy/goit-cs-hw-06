# Використовуємо офіційний образ Python як базовий
FROM python:3.9-slim

# Встановлюємо необхідні пакети
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо необхідні бібліотеки для Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код додатку до контейнера
COPY . /app
WORKDIR /app

# Відкриваємо порти
EXPOSE 3000 5001

# Запускаємо додаток
CMD ["python", "main.py"]
