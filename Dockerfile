FROM python:3.11-slim

WORKDIR /usr/src/app

# Установим gcc для некоторых зависимостей (если потребуется)
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV DATABASE=/usr/src/app/data/mockserver.db

CMD ["flask", "run"]
