# Usa imagem oficial do Python
FROM python:3.9

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos para o container
COPY requirements.txt requirements.txt
COPY app.py app.py

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta 5000 para o tráfego HTTP
EXPOSE 5000

# Comando para rodar o app
CMD ["python", "app.py"]
