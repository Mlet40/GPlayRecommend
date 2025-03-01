import pandas as pd
import numpy as np
from io import BytesIO
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import boto3

# --- CONFIGURAÇÕES DO S3 ---
print('Configuração do S3')
bucket_name = "globoplay-datalak"
# Pasta onde os dados da feature store foram salvos na etapa de ingestão
input_prefix = "featStore/"
# Pasta para salvar os dados treinados
output_prefix = "featStore/trainned/"


s3 = boto3.client("s3")


def load_parquet_from_s3(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    data = response["Body"].read()
    return pd.read_parquet(BytesIO(data))

# --- CARREGAR DADOS PRÉ-PROCESSADOS DA FEATURE STORE ---
# Supondo que o arquivo tenha sido salvo como "featstore_base.parquet"
print('Carregando arquivo parquet')
df_based = load_parquet_from_s3(bucket_name, f"{input_prefix}featstore_base.parquet")

print('Inicio Treinamento')
# --- TREINAMENTO / GERAÇÃO DE FEATURES ---
vec = TfidfVectorizer()
tfidf = vec.fit_transform(df_based['body_clean'].astype(str))
print('Iniciando similaridades')
sim = cosine_similarity(tfidf)
print(len(sim))
sim_df = pd.DataFrame(sim, index=df_based['page'], columns=df_based['page'])

# --- SALVAR A MATRIZ DE SIMILARIDADE NO S3 ---
def save_to_s3(df, filename, prefix=output_prefix):
    buffer = BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)  
    s3.upload_fileobj(buffer, bucket_name, f"{prefix}{filename}")
print('Salvando no s3')


save_to_s3(sim_df, "sim_df.parquet")
