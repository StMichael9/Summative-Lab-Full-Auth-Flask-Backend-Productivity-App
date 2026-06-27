from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from models import db
from schemas import UserSchema, TransactionSchema
from routes import auth_bp, transactions_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "3f9b1c0e8d7a4f2b9c1d0a8e7f6b5c4"


    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(transactions_bp, url_prefix="/transactions")


    @app.route("/")
    def home():
        return {"message": "Backend running"}

    return app
    

if __name__ == "__main__":
    app = create_app()
    app.run(port=5555, debug=True)
