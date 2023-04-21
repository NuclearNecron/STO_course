from app.base.db import db
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class UserModel(db):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nickname = Column(String, unique=True, nullable=False)
    login = Column(String, unique=True, nullable=False)
    password = Column(String, unique=True, nullable=False)

    doc = relationship(
        "DocumentModel",
        back_populates="owner",
        foreign_keys="DocumentModel.owner_id",
    )
    userdocs = relationship(
        "UserDocModel",
        back_populates="user",
        foreign_keys="UserModel.user_id",
    )
