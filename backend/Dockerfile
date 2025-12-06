# Usamos una imagen oficial de Python ligera
FROM python:3.10-slim

# Evita que Python genere archivos .pyc y fuerza salida por consola (logs visibles)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias para audio y postgres
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Comando por defecto (luego lo sobrescribimos en docker-compose si queremos)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]