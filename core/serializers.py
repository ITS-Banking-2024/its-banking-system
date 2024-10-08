# Serializer for the Django customer model
from marshmallow import Schema, fields


class CustomerSerializer(Schema):
    username: fields.Str = fields.Str()


# Serializer for the Django product model
class ProductSerializer(Schema):
    # Define the fields for the product model
    # The as_string=True option is used to ensure that the id is serialized as a string to avoid integer overflow
    id: fields.Integer = fields.Integer(as_string=True)
    name: fields.Str = fields.Str()
    description: fields.Str = fields.Str()
