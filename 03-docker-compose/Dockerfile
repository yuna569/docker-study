FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]