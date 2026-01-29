from flask import Flask, request, jsonify
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

from database import db
from models.user import User
from models.user_meal import Meal
from datetime import datetime, timezone



app = Flask (__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:mysqlPW@127.0.0.1:2200/mysqlDB"
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

db.init_app(app)
with app.app_context():
    db.create_all()

@app.route("/meal/<int:id>/update", methods=["PUT"])
def update_snake(id):
    meal = Meal.query.get(id)  
    if meal is None:
        return jsonify({"Erro": "meal nao encontrada"}), 404
    
    data = request.get_json(silent=True) or {}


    meal.description = data.get("description")
    meal.indicator = data.get("indicator")
    db.session.commit()
    return jsonify({"message": "Atualizado"}), 200


    

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"erro": "Informe email e senha"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or user.password != password:
        return jsonify({"erro": "Credenciais inválidas"}), 401

    login_user(user)  # ✅ agora o current_user vai existir nas próximas requests
    return jsonify({"mensagem": "Login OK", "user_id": user.id}), 200

@app.route("/user/registration",methods=["POST"])
def create_snack():
        
        data = request.get_json(silent=True) or {}
        
        id = data.get("id")
        description = data.get("description")
        indicator = data.get("indicator", True)

        if not description:
         return jsonify({"error": "description is required"}), 400
        
        date_str = data.get("date")  # ex: "2026-01-28T10:30:00Z"
        if date_str:
            try:
                date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except ValueError:
                return jsonify({"error": "date must be ISO-8601"}), 400
        else:
            date = datetime.now(timezone.utc)

        meal = Meal(
        user_id=current_user.id,
        description=description,
        date=date,
        indicator=bool(indicator),
        )
        

        db.session.add(meal)
        db.session.commit()

        return jsonify({
            "id": meal.id,
            "description": meal.description,
            "date": meal.date.isoformat(),
            "indicator": meal.indicator
        }), 201



@app.route("/user", methods=["POST"])
def create_User():
    data = request.get_json(silent=True) or {}

    username = data.get("user")      
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "User, email and password are required"}), 400

    existing_user = User.query.filter(
        (User.email == email) | (User.user == username)
    ).first()

    if existing_user:
        return jsonify({"error": "User or email already exists"}), 409

    new_user = User(user=username, email=email, password=password)  # <-- passa user
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully", "email": email, "user": username}), 201



if __name__ == "__main__":
    app.run(debug=True)