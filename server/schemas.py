from marshmallow import Schema, fields, validates, ValidationError

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password_hash = fields.Str(required=True)

class TransactionSchema(Schema):
    
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    amount = fields.Int(required=True)
    category = fields.Str(required=True)
    date = fields.DateTime(dump_only=True) 
    description = fields.Str()
