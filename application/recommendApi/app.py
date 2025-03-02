      
from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps
import redis

app = Flask(__name__)
app.config['SECRET_KEY'] = 'minha-chave-secreta'  # Substitua por um segredo forte

# Configuração do Redis
# Atualize 'my-redis-cache.ichbon.0001.use1.cache.amazonaws.com' com o endpoint correto
redis_host = "my-redis-cache.ichbon.0001.use1.cache.amazonaws.com"
redis_port = 6379
redis_client = redis.Redis(host=redis_host, port=redis_port)

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
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        return jsonify({'token': token})
    
    return jsonify({'message': 'Usuário ou senha incorretos!!'}), 401


# Rota protegida para realizar a recomendação consultando diretamente o Redis
@app.route('/recommend', methods=['GET'])
@token_required
def recommend():
    param = request.args.get('param')
    if not param:
        return jsonify({'message': 'Parâmetro "param" é obrigatório na query string.'}), 400

    # Define a chave no Redis baseada no parâmetro
    redis_key = f"recommend:{param}"
    result_json = redis_client.get(redis_key)
    if result_json is None:
        return jsonify({'message': f'Nenhuma recomendação encontrada para o parâmetro {param}.'}), 404

    if isinstance(result_json, bytes):
        result_json = result_json.decode('utf-8')
    
    return result_json, 200, {'Content-Type': 'application/json'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

