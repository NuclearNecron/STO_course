from app.base.db import db
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.docs.dataclasses import DocumentDC, UserDocDC


class DocumentModel(db):
    __tablename__ = "document"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    owner_id = Column(
        Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False
    )
    last_edited = Column(DateTime, nullable=False)

    __table_args__ = (UniqueConstraint("name", "owner_id", name="_owner_name"),)

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

    def to_dc(self) -> DocumentDC:
        return DocumentDC(
            id=self.id,
            name=self.name,
            owner_id=self.owner_id,
            last_edited=self.last_edited,
        )


class UserDocModel(db):
    __tablename__ = "userdocs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False
    )
    doc_id = Column(
        Integer, ForeignKey("document.id", ondelete="cascade"), nullable=False
    )
    access = Column(String, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "doc_id", name="_user_doc"),)

    user = relationship(
        "UserModel",
        back_populates="userdocs",
        foreign_keys="UserDocModel.user_id",
    )
    doc = relationship(
        "DocumentModel",
        back_populates="docdetails",
        foreign_keys="UserDocModel.doc_id",
    )

    def to_dc(self) -> UserDocDC:
        return UserDocDC(
            id=self.id,
            user_id=self.user_id,
            doc_id=self.doc_id,
            access=self.access,
        )
