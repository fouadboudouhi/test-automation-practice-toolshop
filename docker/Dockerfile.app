FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY app /app/app

RUN pip install --no-cache-dir \
    fastapi==0.115.0 \
    "pydantic[email]" \
    uvicorn[standard]==0.30.6 \
    sqlalchemy==2.0.34 \
    psycopg[binary]==3.2.1 \
    jinja2==3.1.4

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
