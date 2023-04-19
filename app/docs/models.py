from app.base.db import db
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship


class DocumentModel(db):
    __tablename__ = "document"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable = False)
    path = Column(String, nullable = False)
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="cascade"),
        nullable=False)
    last_edited = Column(DateTime, nullable = False)

    __table_args__ = (
        UniqueConstraint("name", "owner_id", name="_owner_name"),
    )

    owner = relationship(
        "UserModel",
        back_populates="doc",
        foreign_keys="DocumentModel.owner_id",
    )
    docdetails = relationship(
        "UserDocModel",
        back_populates="doc",
        foreign_keys="UserDocModel.doc_id",
    )


class UserDocModel(db):
    __tablename__ = "userdocs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="cascade"),
        nullable=False)
    doc_id = Column(Integer, ForeignKey("document.id", ondelete="cascade"),
        nullable=False)
    access = Column(String, nullable = False)
    __table_args__ = (
        UniqueConstraint("user_id", "doc_id", name="_user_doc"),
    )

    user = relationship(
        "UserModel",
        back_populates="userdocs",
        foreign_keys="UserModel.user_id",
    )
    doc = relationship(
        "DocumentModel",
        back_populates="docdetails",
        foreign_keys="UserDocModel.doc_id",
    )