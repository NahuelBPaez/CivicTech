# Dockerfile.jupyter
FROM python:3.12-slim

WORKDIR /app

# Copiar dependencias e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Exponer puerto de Jupyter
EXPOSE 8888

# Token configurable por variable de entorno (por defecto "civictech" para desarrollo)
ENV JUPYTER_TOKEN=${JUPYTER_TOKEN:-civictech}

# Iniciar Jupyter Lab
CMD ["sh", "-c", "jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=$JUPYTER_TOKEN"]
