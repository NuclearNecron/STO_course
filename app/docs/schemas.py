from marshmallow import Schema, fields


class NewDocSchema(Schema):
    name = fields.Str(required=True)
    timestamp = fields.DateTime(required=True)
