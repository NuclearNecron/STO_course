from marshmallow import Schema, fields


class NewDocSchema(Schema):
    name = fields.Str(required=True)
    timestamp = fields.DateTime(required=True)


class ConnectionSchema(Schema):
    user = fields.Int(required=True)
    rights = fields.Str(required=True)

class UpdDocSchema(Schema):
    data = fields.Dict(required=True)
    text = fields.Str(required=True)