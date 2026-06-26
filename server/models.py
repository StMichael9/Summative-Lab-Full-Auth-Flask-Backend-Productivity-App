from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy import CheckConstraint
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    transactions = db.relationship("Transactions", backref = 'user')

    @validates("username")
    def validate_username(self, key, value):
        if not value or value.strip() == "":
            raise ValueError("Must enter username")
        return value.strip() # saves it cleanly without extra spaces


class Transactions(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, server_default=db.func.now()) # The database will automatically stamp the exact creation time
    description = db.Column(db.Text)

    @validates("amount")
    def validate_amount(self, key, value):
        if value is None or value <= 0:
            raise ValueError("Amount must be greater than 0")
        return value

    @validates("category")
    def validate_category(self, key, value):
        if not value or value.strip() == "":
            raise ValueError("Transaction must have a category")
        return value.strip()

    @validates("date")
    def validate_date(self, key, value):
        # If they leave it blank, let the database default handle it
        if value is None:
            return value
        
        # Convert string to a datetime object if it comes from a web form
        if isinstance(value, str):
            try:
            # Assumes form format is YYYY-MM-DD
                value = datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD.")

        # Financial logic: Prevent future-dated transactions
        if value > datetime.now():
            raise ValueError("Transaction date cannot be in the future.")
        
        return value
