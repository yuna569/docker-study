FROM ubuntu:22.04

RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*
RUN pip install flask

COPY app.py /app.py

ENV FLASK_APP=app
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000

ENTRYPOINT [ "flask", "run" ]

CMD ["--host=$HOST", "--port=$PORT"]
