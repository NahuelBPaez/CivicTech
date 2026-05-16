# Usamos una imagen oficial de Python para 2026
FROM python:3.12-slim

# Instalar dependencias del sistema necesarias para psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Definir el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de librerías e instalarlas
COPY libs.txt .
RUN pip install --no-cache-dir -r libs.txt

# Copiar todo el código del proyecto (db_models/, dao.py, config_vars.py, etc.)
COPY . .

# Exponer el puerto de Jupyter
EXPOSE 8888

# Iniciar Jupyter Lab al levantar el contenedor
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=civictech"]
