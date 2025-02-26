import pandas as pd
import numpy as np
import string
from io import BytesIO
import boto3

# --- CONFIGURAÇÕES DO S3 ---
bucket_name = "globoplay-datalak"
input_prefix = "raw/"         # Pasta com os arquivos de treino e itens
output_prefix = "featStore/"  # Pasta de saída para a feature store



s3 = boto3.client("s3")

def load_csv_from_s3(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    data = response["Body"].read()
    return pd.read_csv(BytesIO(data))

# --- CARREGAR ARQUIVOS DO S3 ---
print("CARREGAR ARQUIVOS DO S3")
response = s3.list_objects_v2(Bucket=bucket_name, Prefix=input_prefix)
all_files = [obj['Key'] for obj in response.get('Contents', [])]

# Seleciona os arquivos de treinamento (contendo "treino" no nome)
print("Seleciona os arquivos de treinamento (contendo treino no nome)")
treino_files = [key for key in all_files if "treino" in key]
dfs_treino = [load_csv_from_s3(bucket_name, key) for key in treino_files]
df_treino = pd.concat(dfs_treino, ignore_index=True)

print("Seleciona os arquivos de itens (contendo itens-parte no nome)")
part_files = [key for key in all_files if "itens-parte" in key]
dfs_part = [load_csv_from_s3(bucket_name, key) for key in part_files]
df_part = pd.concat(dfs_part, ignore_index=True)

# --- PROCESSAMENTO DOS DADOS DE TREINO ---
print("Remove registros indesejados na coluna 'history'")
df_treino = df_treino[~df_treino['history'].str.contains(r"(esid:conteudo_editorial_g1)", na=False, case=False)]
cols_split = ['history', 'timestampHistory', 'numberOfClicksHistory', 'timeOnPageHistory',
              'scrollPercentageHistory', 'pageVisitsCountHistory', 'timestampHistory_new']
for col in cols_split:
    df_treino[col] = df_treino[col].str.split(',')
df_treino = df_treino.explode(cols_split, ignore_index=True)

print("Mescla os dados de treino com os itens")
df = df_treino.merge(df_part, left_on='history', right_on='page', how='left')

# --- PREPARAÇÃO PARA RECOMENDAÇÃO ---
print("reajando a categoria")
df['categoria'] = df['url'].str.extract(r"g1\.globo\.com/([^/]+)/", expand=False).str.lower()
df['categoria'] = df['categoria'].replace({
    'rio-de-janeiro': 'rj', 'sao-paulo': 'sp', 'bahia': 'ba', 'espirito-santo': 'es',
    'minas-gerais': 'mg', 'goias': 'go', 'mato-grosso-do-sul': 'ms', 'mato-grosso': 'mt',
    'pernambuco': 'pe', 'distrito-federal': 'df', 'ceara': 'ce', 'parana': 'pr', 'amazonas': 'am',
    'santa-catarina': 'sc', 'acre': 'ac', None: 'especiais', 'piaui': 'pi', 'rio-grande-do-norte': 'rn',
    'maranhao': 'ma', 'paraiba': 'pb', 'para': 'pa', 'amapa': 'ap', 'alagoas': 'al', 'rondonia': 'ro',
    'rio-grande-do-sul': 'rs'
})
df = df.dropna(subset=['url', 'issued', 'modified', 'title', 'body', 'caption'])

print("selecionadndo quantidade para teinamento")
# Seleciona uma amostra para a próxima etapa
df_based = df.sample(n=30000, random_state=400)

# --- LIMPEZA DO TEXTO ---
print("limpando stopwords")
stop_words = {
    'a', 'alguém', 'alguma', 'algumas', 'alguns', 'ainda', 'além', 'ali', 'anterior', 'antes', 'ao', 'aos', 
    'aquela', 'aquelas', 'aqueles', 'aqui', 'aquilo', 'as', 'assim', 'até', 'através', 'baixo', 'bastante', 
    'bem', 'cada', 'coisa', 'coisas', 'com', 'como', 'completamente', 'conforme', 'contudo', 'comuma', 'da', 
    'dessa', 'desse', 'de', 'debaixo', 'depois', 'devido', 'do', 'dos', 'durante', 'e', 'ela', 'elas', 'ele', 
    'eles', 'em', 'embora', 'enquanto', 'entre', 'era', 'especificamente', 'essa', 'essas', 'esse', 'esses', 
    'esta', 'está', 'estavam', 'estava', 'estou', 'eu', 'fazer', 'fez', 'foi', 'foram', 'força', 'há', 'haver',
    'isto', 'já', 'juntas', 'junto', 'maior', 'mas', 'me', 'menos', 'muita', 'muitas', 'muito', 'muitos', 'na', 
    'nas', 'nem', 'nenhum', 'ninguém', 'no', 'nos', 'nossa', 'nossas', 'nosso', 'nossos', 'não', 'ocorre', 'ou', 
    'outra', 'outras', 'outro', 'outros', 'para', 'parece', 'parte', 'por', 'porque', 'portanto', 'primeiro', 
    'pouco', 'poderia', 'pode', 'podia', 'poderiam', 'quem', 'querer', 'quais', 'quaisquer', 'quase', 'que', 
    'quanto', 'sabe', 'se', 'seja', 'sejam', 'sem', 'sempre', 'sendo', 'seu', 'sua', 'suas', 'são', 'também', 
    'tanto', 'tantos', 'tem', 'temos', 'tempo', 'teu', 'teus', 'ter', 'teriam', 'tinha', 'tivemos', 'todos', 
    'todas', 'todo', 'tudo', 'um', 'uma', 'umas', 'uns', 'vai', 'vão', 'você', 'vocês', 'vez', 'vida', 'viu',
    'fazia', 'realmente', 'porém', 'isso', '.', ','
}

def limpar_descricao(descricao):
    
    palavras = descricao.lower().split()
    palavras_limpa = [palavra for palavra in palavras if palavra not in stop_words and palavra not in string.punctuation]
    return ' '.join(palavras_limpa)

df_based['body_clean'] = df_based['body'].apply(limpar_descricao)

# --- SALVAR O RESULTADO NA FEATURE STORE ---
def save_to_s3(df, filename, prefix=output_prefix):
    buffer = BytesIO()
    df.to_parquet(buffer, index=False)
    s3.put_object(Bucket=bucket_name, Key=f"{prefix}{filename}", Body=buffer.getvalue())
print("salvando no s3")
# Exemplo: salvar o DataFrame pré-processado (featstore base) em formato Parquet
save_to_s3(df_based, "featstore_base.parquet")
