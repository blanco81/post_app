# Selecciona la imagen base con la versión de Python adecuada
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo requirements.txt al contenedor
COPY requirements.txt .

# Instala las dependencias del sistema necesarias y luego instala Python requirements
RUN apt-get update && apt-get install -y build-essential libpq-dev && \
    pip install --no-cache-dir -r requirements.txt --timeout=100 --retries=5

# Copia todo el contenido del proyecto al contenedor
COPY . .

# Expone el puerto en el que se ejecutará la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
