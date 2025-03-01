from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps
import pandas as pd
import s3fs  # Necessário para ler o Parquet diretamente do S3
from flask_caching import Cache

app = Flask(__name__)
app.config['SECRET_KEY'] = 'minha-chave-secreta'  # Substitua por um segredo forte

# Configuração do Flask-Caching para usar Redis
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_HOST'] = 'redis'           # Nome ou IP do host Redis (ajuste conforme seu ambiente)
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_REDIS_DB'] = 0
app.config['CACHE_DEFAULT_TIMEOUT'] = 3600         # Tempo de expiração do cache (1 hora)
cache = Cache(app)

# Middleware para verificar JWT
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

# Rota de login (gera JWT)
@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Credenciais inválidas'}), 401
    
    # Usuário e senha fixos para teste
    if auth['username'] == 'admin' and auth['password'] == '1234':
        token = jwt.encode({
            'user': auth['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Expira em 1 hora
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({'token': token})
    
    return jsonify({'message': 'Usuário ou senha incorretos!!'}), 401

# Função para carregar e cache o DataFrame usando Redis
@cache.memoize(timeout=3600)  # Cache por 1 hora
def get_df_cache():
    # Essa função é chamada apenas uma vez a cada período de cache,
    # e o resultado é serializado e armazenado no Redis.
    df = pd.read_parquet("s3://globoplay-datalak/featStore/trainned/sim_df.parquet")
    return df
    

# Rota protegida para realizar a recomendação
@app.route('/recommend', methods=['GET'])
@token_required
def recommend():
    param = request.args.get('param')
    if not param:
        return jsonify({'message': 'Parâmetro "param" é obrigatório na query string.'}), 400

    try:
        df_cache = get_df_cache()
    except Exception as e:
        return jsonify({'message': 'Erro ao carregar dados do cache.', 'error': str(e)}), 500
    
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
