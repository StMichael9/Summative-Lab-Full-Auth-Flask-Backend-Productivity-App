from flask import Blueprint, request, session
from models import db, Transaction
from schemas import TransactionSchema
from marshmallow import Schema, fields, validate, ValidationError
transactions_bp = Blueprint("transactions_bp", __name__)

class CreateTransactionSchema(Schema):
    amount = fields.Float(required=True, validate=validate.Range(min=0.01, error="Amount must be greater than zero."))
    category = fields.String(required=True, validate=validate.Length(min=1, error="Cannot be empty"))
    description = fields.String(required=False, allow_none=True)

class UpdateTransactionSchema(CreateTransactionSchema):
    class Meta:
        # Automatically copies all fields from CreateTransactionSchema
        # but strips away the "required=True" rule from them for PATCH requests.
        partial = True       
        
create_schema = CreateTransactionSchema()
update_schema = UpdateTransactionSchema()

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
    
    data = request.get_json()
    if data is None:
        return {"error": "Missing JSON payload"}, 400

    try:
        validated_data = create_schema.load(data)
    except ValidationError as err:
        return {"errors": err.messages}, 400

    new_transaction = Transaction(
        amount=validated_data["amount"],
        category=validated_data["category"],
        description=validated_data.get("description"),
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

    data = request.get_json() 
    if data is None:
        return {"error": "Missing JSON payload"}, 400
    
    try:
        validated_data = update_schema.load(data)
    except ValidationError as err:
        return {"errors": err.messages}, 400

    for field in ["amount", "category", "description"]:
        if field in validated_data:
            setattr(transaction, field, validated_data[field])

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
