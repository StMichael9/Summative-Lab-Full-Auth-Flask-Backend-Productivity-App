from flask import Blueprint, request, session
from models import db, Transaction
from schemas import TransactionSchema

transactions_bp = Blueprint("transactions_bp", __name__)

@transactions_bp.route("", methods=["GET"])
def get_transactions():
    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401
    transactions = Transaction.query.filter_by(user_id=session["user_id"]).all()
    return TransactionSchema(many=True).dump(transactions), 200

@transactions_bp.route("", methods=["POST"])
def create_transaction():
    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401

    data = request.get_json() or {}

    new_transaction = Transaction(
        amount=data["amount"],
        category=data["category"],
        description=data.get("description"),
        user_id=session["user_id"]
    )

    db.session.add(new_transaction)
    db.session.commit()

    return TransactionSchema().dump(new_transaction), 201

@transactions_bp.route("/<int:id>", methods=["PATCH"])
def update_transaction(id):
    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401

    transaction = Transaction.query.get(id)
    if not transaction:
        return {"error": "Transaction not found"}, 404

    if transaction.user_id != session["user_id"]:
        return {"error": "Unauthorized"}, 401

    data = request.get_json() or {}

    for field in ["amount", "category", "description"]:
        if field in data:
            setattr(transaction, field, data[field])

    db.session.commit()
    return TransactionSchema().dump(transaction), 200

@transactions_bp.route("/<int:id>", methods=["DELETE"])
def delete_transaction(id):
    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401

    transaction = Transaction.query.get(id)
    if not transaction:
        return {"error": "Transaction not found"}, 404

    if transaction.user_id != session["user_id"]:
        return {"error": "Unauthorized"}, 401

    db.session.delete(transaction)
    db.session.commit()

    return {}, 204
