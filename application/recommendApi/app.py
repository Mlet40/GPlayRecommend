from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'minha-chave-secreta'  # Substitua por um segredo forte

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
    return jsonify({"message": "Hello, World! API rodando no ECS Fargate!"})

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

# Rota protegida por JWT
@app.route('/protected', methods=['GET'])
@token_required
def protected():
    return jsonify({"message": "Você acessou um endpoint protegido!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Escuta em todas as interfaces
