from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    """
    schema for validating input on register and login endpoints
    """
    id = fields.Int(dump_only=True)
    email = fields.Str(required=True, validate=validate.Email())
    password = fields.Str(required=True, validate=validate.Length(min=8))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
