from flask import request, session, jsonify
from . import auth_bp
from models import db, User
from schemas import UserSchema


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user:
        return {"error": "User already exists"}, 422
    
    new_user = User(username=username)
    new_user.password_hash = password
    db.session.add(new_user)
    db.session.commit()
    # Signs the user in
    session["user_id"] = new_user.id
    user_data = UserSchema().dump(new_user)
    return user_data, 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if not user or not user.authenticate(password):
        return {"error": "Invalid username or password"}, 401
    session['user_id'] = user.id
    return UserSchema().dump(user), 200

@auth_bp.route("/logout", methods=["DELETE"])
def logout():
    session.clear()
    return {}, 200

@auth_bp.route("/check_session", methods=["GET"])
def check_session():
    user_id = session.get("user_id")
    if not user_id:
        return {}, 204
    user = User.query.get(user_id)
    return UserSchema().dump(user), 200
