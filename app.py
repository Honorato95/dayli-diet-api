from datetime import datetime, timezone
from flask import Flask, jsonify, request
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from database import db
from models.user import User
from models.meal import Meal
import bcrypt

app = Flask(__name__)
app.config["SECRET_KEY"] = "password"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:administrator@127.0.0.1:3307/daily-diet-API"
db.init_app(app)

# Criação de um novo usuário
@app.route("/user", methods=["POST"])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Usuário cadastrado."}), 201

    return jsonify({"message": "Informações inválidas"}), 400

# Atualiza username e senha do usuário logado.
@app.route("/user/<int:id_user>", methods=["PUT"])
@login_required
def update_user(id_user):
    data = request.json
    user = User.query.get(id_user)

    if id_user != current_user.id:
        return jsonify({"message": "Operação não permitida"}), 403

    if user:
        user.username = data.get("username")
        user.password = bcrypt.hashpw(str.encode(data.get("password")), bcrypt.gensalt())
        db.session.commit()
        return jsonify({"message": f"Nome de usário e/ou senha alterado para usuário {user.username}"})
    

    return jsonify({"message":"Usuário não encontrado"}), 404

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Checagem de qual usário está logado
@app.route("/current", methods=["GET"])
def current_user_info():
    if current_user.is_authenticated:
        return jsonify({"username": current_user.username})
    return jsonify({"message": "Usuário não autenticado."}), 401

# Rota de login para usuário que irá gerenciar suas refeições
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if username and password:
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            login_user(user)
            return jsonify({"message": "Autenticação realizada."})
        
    return jsonify({"message": "Credenciais inválidas."}), 404

# Carrega o usuário a partir do ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Logout do usuário
@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout realizado."})

# Criação de uma nova refeição
@app.route("/meal", methods=["POST"])
@login_required
def create_meal():
    data = request.json
    name = data.get("name")
    description = data.get("description")
    in_diet = data.get("in_diet")

    if name and description:
        meal = Meal(name=name, description=description, in_diet=in_diet, user_id=current_user.id)
        db.session.add(meal)
        db.session.commit()
        return jsonify({"message": "Refeição adicionada."}), 201
    
    return jsonify({"message":"Insira todas as informções."}), 400

# Atualiza informações da refeição criada pelo usuário logado
@app.route("/meal/<int:id_meal>", methods=["PUT"])
@login_required
def edit_meal(id_meal):
    data = request.json
    meal = Meal.query.get(id_meal)

    if  meal.user_id != current_user.id:
        return jsonify({"message": "Operação não permitida"}), 403
    else:
        meal.name = data.get("name", meal.name)
        meal.description = data.get("description", meal.description)
        meal.in_diet = data.get("in_diet", meal.in_diet)
        meal.data_time = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({"message": "Refeição atualizada com sucesso"})

# Retorna todas as refeições criadas pelo usário logado
@app.route("/meal", methods=["GET"])
@login_required
def get_meals():
    meals = Meal.query.all()
    if meals:
        meals_data = [meal.to_dict() for meal in meals if meal.user_id == current_user.id]
        return jsonify(meals_data)

    return jsonify({"message": "Nenhuma refeição encontrada."}), 404

# Busca uma refeição específica criada pelo usário logado
@app.route("/meal/<int:id_meal>", methods=["GET"])
@login_required
def get_meal(id_meal):
    meal = Meal.query.get(id_meal)

    if meal and meal.user_id == current_user.id:
        return jsonify(meal.to_dict())
    
    return jsonify({"message": "Refeição não encontrada."}), 404

# Deleta uma refeição criada pelo usuário logado
@app.route("/meal/<int:id_meal>", methods=["DELETE"])
@login_required
def delete_meal(id_meal):
    meal = Meal.query.get(id_meal)

    if meal and meal.user_id == current_user.id:
        db.session.delete(meal)
        db.session.commit()
        return jsonify({"message": "Refeição deletada com sucesso."})

    return jsonify({"message": "Refeição não encontrada."}), 404

if __name__ == "__main__":
    app.run()