FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV OCR_BACKEND=ocrspace
CMD exec gunicorn -w 2 -b 0.0.0.0:$PORT app:app
