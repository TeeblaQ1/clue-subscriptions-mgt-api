from marshmallow import Schema, fields, validate

class SubscriptionPlanSchema(Schema):
    """
    schema for validating input on create subscription plan endpoint
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    description = fields.Str(required=False, validate=validate.Length(min=1))
    price_cents = fields.Int(required=True, validate=validate.Range(min=0))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class SubscriptionSchema(Schema):
    """
    schema for validating input on subscribe endpoint
    """
    id = fields.Int(dump_only=True)
    plan_id = fields.Int(required=True, validate=validate.Range(min=1))
    duration_days = fields.Int(required=True, validate=validate.Range(min=1))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)