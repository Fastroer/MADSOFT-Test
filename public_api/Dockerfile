FROM python:3.12

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

CMD ["sh", "-c", "alembic -c /app/db/alembic.ini upgrade head && uvicorn main:public_app --host 0.0.0.0 --port 8000"]
