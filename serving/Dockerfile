FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Garde ces lignes ! Elles sont indispensables pour cette image spécifique.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le code de l'API et surtout tes modèles .pickle
COPY . .

EXPOSE 8080

# Utilise uvicorn pour lancer api.py
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]