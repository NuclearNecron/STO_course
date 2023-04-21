from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(required=False)
    nickname = fields.Str(required=False)
    login = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class NewUserSchema(Schema):
    id = fields.Int(required=False)
    nickname = fields.Str(required=True)
    login = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
