FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      rclone ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .

ENV PYTHONUNBUFFERED=1
ENV RCLONE_CONFIG=/config/rclone/rclone.conf

CMD ["python", "bot.py"]
