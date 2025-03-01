from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps
import pandas as pd
import s3fs  # Necessário para que o pandas leia diretamente do S3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'minha-chave-secreta'  # Substitua por um segredo forte

# Variável global para armazenar o DataFrame em cache
df_cache = None

# Middleware para verificar JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token ausente!'}), 403
        try:
            token = token.split(" ")[1]  # Remove 'Bearer ' do token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except Exception as e:
            return jsonify({'message': 'Token inválido!', 'error': str(e)}), 403
        return f(*args, **kwargs)
    return decorated

# Rota pública
@app.route('/')
def hello():
    return jsonify({"message": "Hello, World! API rodando no ECS Service com Flask!"})

# Rota de login (gera JWT)
@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Credenciais inválidas'}), 401
    
    # Usuário e senha fixos para teste
    if auth['username'] == 'appClient' and auth['password'] == '1234':
        token = jwt.encode({
            'user': auth['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Expira em 1 hora
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({'token': token})
    
    return jsonify({'message': 'Usuário ou senha incorretos!!'}), 401

# Carregar o arquivo Parquet em cache ao iniciar a aplicação
@app.before_first_request
def load_parquet():
    global df_cache
    try:
        # Lê o arquivo Parquet diretamente do S3 usando s3fs
        df_cache = pd.read_parquet("s3://globoplay-datalak/featStore/trainned/sim_df.parquet")
        app.logger.info(f"Arquivo Parquet carregado com sucesso. Shape: {df_cache.shape}")
    except Exception as e:
        app.logger.error("Erro ao carregar o arquivo Parquet: %s", e)
        # Opcional: Você pode optar por não levantar exceção aqui para que a API inicie mesmo sem dados

# Rota protegida para recomendar usando o TF-IDF treinado
@app.route('/recommend', methods=['GET'])
@token_required
def recommend():
    global df_cache
    param = request.args.get('param')
    if not param:
        return jsonify({'message': 'Parâmetro "param" é obrigatório na query string.'}), 400

    if df_cache is None:
        return jsonify({'message': 'Arquivo de dados não carregado.'}), 500
    
    if param not in df_cache.columns:
        return jsonify({'message': f'Parâmetro "{param}" não encontrado nos dados.'}), 400
    
    try:
        # Ordena os valores da coluna especificada em ordem decrescente
        sorted_series = df_cache[param].sort_values(ascending=False)
        # Converte a Series ordenada em DataFrame
        result_df = pd.DataFrame(sorted_series)
        # Converte o DataFrame para JSON no formato de lista de registros
        result_json = result_df.to_json(orient="records")
        return result_json, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({'message': 'Erro ao processar a requisição.', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
