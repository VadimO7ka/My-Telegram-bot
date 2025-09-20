FROM python:3.11-slim

WORKDIR /bot

# Копируем зависимости
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Копируем весь код
COPY . .

CMD ["python", "bot.py"]
