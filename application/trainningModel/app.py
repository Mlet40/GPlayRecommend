import pandas as pd  
import numpy as np
from io import BytesIO
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import boto3
import redis
import pickle


def save_to_redis(sim_df):    

    # --- CONFIGURAÇÃO DO REDIS ---
    # Como o ElastiCache Redis foi provisionado sem auth_token,
    # não precisamos passar usuário ou senha.
    redis_host = "my-redis-cache.ichbon.0001.use1.cache.amazonaws.com:6379"  # Exemplo: "redis.mycompany.cache.amazonaws.com" ou "localhost"
    redis_port = 6379

    # Cria o cliente Redis sem autenticação
    redis_client = redis.Redis(host=redis_host, port=redis_port)

    # --- ARMAZENAR A MATRIZ DE SIMILARIDADE NO REDIS ---
    # Serializa o DataFrame usando pickle.
    redis_key = "sim_df"
    print('Serializando e salvando o DataFrame no Redis...')
    serialized_data = pickle.dumps(sim_df)
    redis_client.set(redis_key, serialized_data)

def load_parquet_from_s3(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    data = response["Body"].read()
    return pd.read_parquet(BytesIO(data))
    
 # --- SALVAR A MATRIZ DE SIMILARIDADE NO S3 ---
def save_to_s3(df, filename, prefix=output_prefix):
    buffer = BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)
    s3.upload_fileobj(buffer, bucket_name, f"{prefix}{filename}")   

# --- CONFIGURAÇÕES DO S3 ---
print('Configuração do S3')
bucket_name = "globoplay-datalak"
# Pasta onde os dados da feature store foram salvos na etapa de ingestão
input_prefix = "featStore/"
# Pasta para salvar os dados treinados
output_prefix = "featStore/trainned/"

s3 = boto3.client("s3")

# --- CARREGAR DADOS PRÉ-PROCESSADOS DA FEATURE STORE ---
# Supondo que o arquivo tenha sido salvo como "featstore_base.parquet"
print('Carregando arquivo parquet')
df_based = load_parquet_from_s3(bucket_name, f"{input_prefix}featstore_base.parquet")

print('Início do Treinamento')
# --- TREINAMENTO / GERAÇÃO DE FEATURES ---
vec = TfidfVectorizer()
tfidf = vec.fit_transform(df_based['body_clean'].astype(str))
print('Calculando similaridades')
sim = cosine_similarity(tfidf)
print('Número de similaridades calculadas:', len(sim))
sim_df = pd.DataFrame(sim, index=df_based['page'], columns=df_based['page'])

print('Salvando arquivo Parquet no S3')
save_to_s3(sim_df, "sim_df.parquet")

print('Salvando arquivo Redis')
save_to_redis(sim_df)

print("Processo concluído com sucesso.")
