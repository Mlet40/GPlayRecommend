##--- PASSO 1: GERAR FEATURES E SALVAR NO S3 ---
import pandas as pd
import boto3
from io import BytesIO

from feast import Entity, FeatureView, Field
from feast.types import Int64, Float64, String  # Importando os novos tipos
from feast.infra.offline_stores.file_source import FileSource

# Configurações do S3
bucket_name = "globoplay-datalak"
input_key = "raw/dados_teste.csv"  # Caminho do CSV de entrada
output_prefix = "poc/"

# Criar cliente S3
s3 = boto3.client("s3")

# Carregar os dados do CSV diretamente do S3
response = s3.get_object(Bucket=bucket_name, Key=input_key)
data = response["Body"].read()
df = pd.read_csv(BytesIO(data))
df.columns = df.columns.str.strip()  # Remove espaços extras

# Se as colunas já estiverem corretas, não é necessário renomeá-las.
# Caso queira confirmar, você pode imprimir as colunas:
print("Colunas do DataFrame:", df.columns)

# Criar categorias com base no URL
df["categoria"] = df["url"].apply(
    lambda x: "Esporte" if "esporte" in x.lower() else "Internacional" if "internacional" in x.lower() else "Regional"
)

# Criar Features dos Usuários
user_features = df.groupby("userId").agg(
    número_de_noticias_lidas=("titulo", "count"),
    tempo_médio_leitura=("tempo_leitura_segundos", "mean"),
    categorias_lidas=("categoria", lambda x: list(set(x)))
).reset_index()

# Criar Features das Notícias
news_features = df.groupby("titulo").agg(
    tempo_médio_leitura=("tempo_leitura_segundos", "mean"),
    popularidade=("titulo", "count"),
    categoria=("categoria", "first")
).reset_index()

# Função para salvar no S3 em Parquet
def save_to_s3(df, filename):
    buffer = BytesIO()
    df.to_parquet(buffer, index=False)
    s3.put_object(Bucket=bucket_name, Key=f"{output_prefix}{filename}", Body=buffer.getvalue())
    print(f"✅ Arquivo salvo: s3://{bucket_name}/{output_prefix}{filename}")

# Salvar Features no S3
save_to_s3(user_features, "user_features.parquet")
save_to_s3(news_features, "news_features.parquet")

print("✅ Features geradas e salvas no S3 em Parquet!")
