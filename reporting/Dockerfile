FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8082

CMD python project.py && evidently ui --host 0.0.0.0 --port 8082