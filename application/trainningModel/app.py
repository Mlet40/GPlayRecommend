import pandas as pd  
import numpy as np
from io import BytesIO
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import boto3
import redis
import pickle
import math

# --- CONFIGURAÇÃO DO REDIS ---
redis_host = "my-redis-cache.ichbon.0001.use1.cache.amazonaws.com"  # Exemplo: "redis.mycompany.cache.amazonaws.com" ou "localhost"
redis_port = 6379
redis_client = redis.Redis(host=redis_host, port=redis_port)

# --- CONFIGURAÇÕES DO S3 ---
print('Configuração do S3')
bucket_name = "globoplay-datalak"
# Pasta onde os dados da feature store foram salvos na etapa de ingestão
input_prefix = "featStore/"
# Pasta para salvar os dados treinados
output_prefix = "featStore/trainned/"
s3 = boto3.client("s3")

# Função para resetar o cache do Redis (somente as chaves de recomendação)
def reset_recommendations_cache():
    # Obtém todas as chaves que começam com "recommend:"
    keys = redis_client.keys("recommend:*")
    if keys:
        redis_client.delete(*keys)
        print(f"Chaves apagadas: {[key.decode('utf-8') for key in keys]}")
    else:
        print("Nenhuma chave de recomendação encontrada para apagar.")

# Função para salvar as recomendações no Redis (top 10 por coluna, com page e score)
def save_recommendations_to_redis(sim_df,df_based):
    
    df_based_filtered = df_based[["page","url", "issued", "title"]]
    df_based_filtered = df_based_filtered.set_index("page")
    
    for param in sim_df.columns:
       
        sorted_series = sim_df[param].sort_values(ascending=False).head(10)

        df_recommend = sorted_series.reset_index()
        df_recommend.columns = ["page", "score"]
        
        df_recommend['page'] = df_recommend['page'].astype(str)
        df_based_filtered.index = df_based_filtered.index.astype(str)
        
        df_merged = df_recommend.merge(df_based_filtered, left_on="page", right_index=True, how="left")

        # Converte o DataFrame para JSON
        result_json = df_merged.to_json(orient="records")
        # Salva no Redis com a chave "recommend:{param}"
        redis_key = f"recommend:{param}"
        redis_client.set(redis_key, result_json)
        print(f"Salvou recomendação para '{param}' em {redis_key}.")


def save_dataframe_in_chunks(df, base_key, chunk_size=1000):
    # Divide o DataFrame em chunks de "chunk_size" linhas
    total_rows = df.shape[0]
    total_chunks = math.ceil(total_rows / chunk_size)
    # Cria o cliente Redis sem autenticação
    redis_client = redis.Redis(host=redis_host, port=redis_port)
    
    for i in range(total_chunks):
        chunk_df = df.iloc[i*chunk_size:(i+1)*chunk_size]
        serialized_chunk = pickle.dumps(chunk_df)
        redis_key = f"{base_key}_chunk_{i}"
        redis_client.set(redis_key, serialized_chunk)
        print(f"Salvou chunk {i} com {chunk_df.shape[0]} linhas.")

    # Opcional: armazenar metadados para recompor os chunks
    redis_client.set(f"{base_key}_chunks_count", total_chunks)


def save_to_redis(sim_df):    
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
def save_to_s3(df, filename, prefix):
    buffer = BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)
    s3.upload_fileobj(buffer, bucket_name, f"{prefix}{filename}")   


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
save_to_s3(sim_df, "sim_df.parquet",output_prefix)

print('Salvando arquivo Redis')
print("Resetando o cache de recomendações no Redis...")
reset_recommendations_cache()

print("Salvando as novas recomendações no Redis...")
save_recommendations_to_redis(sim_df,df_based)
