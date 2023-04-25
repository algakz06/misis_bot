FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y curl gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN mkdir -p ./logs

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "-m", "app"]
