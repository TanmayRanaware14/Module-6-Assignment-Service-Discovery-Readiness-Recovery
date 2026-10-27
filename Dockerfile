FROM python:3.12-slim

WORKDIR /app
COPY inventory_service/server.py /app/server.py
COPY client/client.py /app/client.py

ENV PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["python", "/app/server.py"]
