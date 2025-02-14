# Escolha uma imagem base Python
FROM python:3.9-slim

# Crie uma pasta de trabalho
WORKDIR /app

# Copie requirements e instale
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie o resto do código
COPY app.py .

# Comando de execução do script (imprime Hello World)
CMD ["python", "app.py"]
