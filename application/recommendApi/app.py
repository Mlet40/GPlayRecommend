from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps
import pandas as pd
import redis
import pickle

app = Flask(__name__)
app.config['SECRET_KEY'] = 'minha-chave-secreta'  # Substitua por um segredo forte

# Configuração do Redis
# Atualize 'redis' com o endpoint correto se necessário.
redis_host = "my-redis-cache.ichbon.0001.use1.cache.amazonaws.com"  
redis_port = 6379
redis_client = redis.Redis(host=redis_host, port=redis_port)


def load_dataframe_from_chunks(base_key):
    """
    Recupera os chunks armazenados no Redis e reconstrói o DataFrame completo.
    """
    chunks_count = redis_client.get(f"{base_key}_chunks_count")
    if chunks_count is None:
        print("Número de chunks não encontrado no Redis.")
        return None
    chunks_count = int(chunks_count)
    
    df_list = []
    for i in range(chunks_count):
        redis_key = f"{base_key}_chunk_{i}"
        serialized_chunk = redis_client.get(redis_key)
        if serialized_chunk is None:
            print(f"Chunk {i} não encontrado no Redis.")
            continue
        # Desserializa o chunk
        chunk_df = pickle.loads(serialized_chunk)
        df_list.append(chunk_df)
    
    if df_list:
        df = pd.concat(df_list, ignore_index=True)
        return df
    else:
        print("Nenhum chunk foi carregado.")
        return None

# Middleware para verificação do JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token ausente!'}), 403
        try:
            token = token.split(" ")[1]  # Remove 'Bearer ' do token
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except Exception as e:
            return jsonify({'message': 'Token inválido!', 'error': str(e)}), 403
        return f(*args, **kwargs)
    return decorated

# Rota pública
@app.route('/')
def hello():
    return jsonify({"message": "Hello, World! API rodando no ECS com Flask e Redis!"})

# Rota de login para gerar JWT
@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Credenciais inválidas'}), 401
    
    # Usuário e senha fixos para teste
    if auth['username'] == 'admin' and auth['password'] == '1234':
        payload = {
            'user': auth['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")
        # Converte para string caso o token seja bytes
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        return jsonify({'token': token})
    
    return jsonify({'message': 'Usuário ou senha incorretos!!'}), 401

# Rota protegida para recomendar utilizando os dados armazenados em Redis
@app.route('/recommend', methods=['GET'])
@token_required
def recommend():
    param = request.args.get('param')
    if not param:
        return jsonify({'message': 'Parâmetro "param" é obrigatório na query string.'}), 400

    try:
        df_cache = load_dataframe_from_chunks("sim_df")
    except Exception as e:
        return jsonify({'message': 'Erro ao carregar dados do cache.', 'error': str(e)}), 500
    
    if df_cache is None:
        return jsonify({'message': 'Nenhum dado carregado do cache Redis.'}), 500
    
    if param not in df_cache.columns:
        return jsonify({'message': f'Parâmetro "{param}" não encontrado nos dados.'}), 400

    try:
        # Ordena os valores da coluna especificada em ordem decrescente
        sorted_series = df_cache[param].sort_values(ascending=False)
        result_df = pd.DataFrame(sorted_series)
        result_json = result_df.to_json(orient="records")
        return result_json, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({'message': 'Erro ao processar a requisição.', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
