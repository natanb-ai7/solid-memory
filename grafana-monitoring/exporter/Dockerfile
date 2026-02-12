FROM python:3.11.8-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

RUN useradd --create-home --shell /usr/sbin/nologin exporter

COPY openclaw_exporter.py /app/openclaw_exporter.py

USER exporter

EXPOSE 9091

CMD ["python", "/app/openclaw_exporter.py"]
