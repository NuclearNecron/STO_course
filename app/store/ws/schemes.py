from marshmallow import Schema, fields, post_load

from app.store.ws.dataclasses import Event


class EventSchema(Schema):
    type = fields.Str(required=True)
    payload = fields.Dict(required=True)

    @post_load
    def make_Event(self, data, **kwargs) -> Event:
        return Event(**data)
