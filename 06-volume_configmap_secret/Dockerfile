FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies for the FastAPI file server.
RUN pip install --no-cache-dir fastapi "uvicorn[standard]" python-multipart

COPY app.py ./

ENV PORT=3000
ENV UPLOAD_DIR=/data/uploads

RUN mkdir -p "$UPLOAD_DIR"

EXPOSE 3000

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-3000}"]
