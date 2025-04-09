import os
import json
import hashlib
from flask_login import UserMixin

# Caminho para o arquivo de configuração dos usuários
USERS_FILE = 'users.json'

class User(UserMixin):
    def __init__(self, id, username, email, password_hash=None, is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin
    
    def check_password(self, password):
        """Verifica se a senha fornecida corresponde ao hash armazenado"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return password_hash == self.password_hash
    
    @staticmethod
    def hash_password(password):
        """Cria um hash simples da senha"""
        return hashlib.sha256(password.encode()).hexdigest()

def get_users():
    """Retorna todos os usuários do arquivo de configuração"""
    if not os.path.exists(USERS_FILE):
        # Cria um usuário padrão se o arquivo não existir
        default_users = {
            "1": {
                "username": "admin",
                "email": "admin@example.com",
                "password_hash": User.hash_password("admin123"),
                "is_admin": True
            },
            "2": {
                "username": "ddt",
                "email": "ddt@ddt.com.br",
                "password_hash": User.hash_password("Tiburcio50"),
                "is_admin": True
            }
        }
        with open(USERS_FILE, 'w') as f:
            json.dump(default_users, f, indent=4)
        return default_users
    
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def get_user(user_id):
    """Retorna um usuário pelo ID"""
    users = get_users()
    user_data = users.get(str(user_id))
    
    if user_data:
        return User(
            id=user_id,
            username=user_data['username'],
            email=user_data.get('email', ''),
            password_hash=user_data['password_hash'],
            is_admin=user_data.get('is_admin', False)
        )
    return None

def get_user_by_email(email):
    """Retorna um usuário pelo email"""
    users = get_users()
    
    for user_id, user_data in users.items():
        if user_data.get('email') == email:
            return User(
                id=user_id,
                username=user_data['username'],
                email=user_data.get('email', ''),
                password_hash=user_data['password_hash'],
                is_admin=user_data.get('is_admin', False)
            )
    return None

def get_user_by_username(username):
    """Retorna um usuário pelo nome de usuário"""
    users = get_users()
    
    for user_id, user_data in users.items():
        if user_data['username'] == username:
            return User(
                id=user_id,
                username=user_data['username'],
                email=user_data.get('email', ''),
                password_hash=user_data['password_hash'],
                is_admin=user_data.get('is_admin', False)
            )
    return None

def add_user(username, email, password, is_admin=False):
    """Adiciona um novo usuário"""
    users = get_users()
    
    # Verifica se o usuário ou email já existe
    for user_data in users.values():
        if user_data['username'] == username or user_data.get('email') == email:
            return False
    
    # Gera um novo ID
    new_id = str(max([int(id) for id in users.keys()], default=0) + 1)
    
    # Adiciona o novo usuário
    users[new_id] = {
        "username": username,
        "email": email,
        "password_hash": User.hash_password(password),
        "is_admin": is_admin
    }
    
    # Salva no arquivo
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)
    
    return True

def edit_user(user_id, new_username=None, new_email=None, new_password=None, is_admin=None):
    """Edita um usuário existente"""
    users = get_users()
    
    # Verifica se o ID existe
    if user_id not in users:
        return False
    
    # Verifica se o novo nome de usuário já existe (se estiver sendo alterado)
    if new_username and new_username != users[user_id]['username']:
        for other_id, user_data in users.items():
            if other_id != user_id and user_data['username'] == new_username:
                return False
    
    # Verifica se o novo email já existe (se estiver sendo alterado)
    if new_email and new_email != users[user_id].get('email'):
        for other_id, user_data in users.items():
            if other_id != user_id and user_data.get('email') == new_email:
                return False
    
    # Atualiza os dados
    if new_username:
        users[user_id]['username'] = new_username
    
    if new_email:
        users[user_id]['email'] = new_email
    
    if new_password:
        users[user_id]['password_hash'] = User.hash_password(new_password)
    
    if is_admin is not None:
        users[user_id]['is_admin'] = is_admin
    
    # Salva no arquivo
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)
    
    return True

def delete_user(user_id):
    """Remove um usuário"""
    users = get_users()
    
    # Verifica se o ID existe
    if user_id not in users:
        return False
    
    # Impede a remoção dos usuários padrão
    if user_id in ["1", "2"]:
        return False
    
    # Remove o usuário
    del users[user_id]
    
    # Salva no arquivo
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)
    
    return True
