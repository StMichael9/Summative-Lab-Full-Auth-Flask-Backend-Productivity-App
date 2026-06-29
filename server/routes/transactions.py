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
    # Pagination
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int) 
      
    query = Transaction.query.filter_by(user_id=session["user_id"])
    
    # Sorting
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')
    if hasattr(Transaction, sort):
        column = getattr(Transaction, sort)
        if order == "desc":
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

    # Filtering
    # Get all column names from the model
    model_columns = Transaction.__table__.columns.keys()

# Loop through every query parameter the user sent
    for key, value in request.args.items():
        # Skip pagination and sorting params
        if key in ["page", "limit", "sort", "order"]:
                continue

        # If the key matches a column, apply a filter
        if key in model_columns:
            query = query.filter(getattr(Transaction, key) == value)

    transactions = query.paginate(page=page, per_page=limit, error_out=False) 
    return TransactionSchema(many=True).dump(transactions.items), 200

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

    for field, value in validated_data.items():
        setattr(transaction, field, value)


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
