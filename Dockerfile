FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Копируем всё
COPY . .

# Проверяем что файл есть
RUN ls -la

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD sh -c "python main.py & python health.py"
