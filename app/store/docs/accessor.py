from dataclasses import asdict
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, List

import sqlalchemy.exc
from sqlalchemy import select, desc, update, delete, func
from sqlalchemy.orm import selectinload

from app.base.base_accessor import BaseAccessor
from app.docs.dataclasses import (
    DocumentDC,
    UserDocDC,
    fullDoc,
    UserforDoc,
    fullAccess,
)
from app.docs.models import DocumentModel, UserDocModel


class DocsAccessor(BaseAccessor):
    async def create_doc(
        self, name: str, owner_id: int, timestamp: datetime = datetime.now()
    ) -> DocumentDC | None:
        try:
            async with self.app.database.session() as session:
                new_doc = DocumentModel(
                    name=name, owner_id=owner_id, last_edited=timestamp
                )
                session.add(new_doc)
                await session.commit()
                return new_doc.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None

    async def check_ownership(
        self, doc_id: int, user_id: int
    ) -> DocumentDC | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    select(DocumentModel)
                    .where(
                        (DocumentModel.id == doc_id)
                        and (DocumentModel.owner_id == user_id)
                    )
                    .limit(1)
                )
                res = await session.scalars(query)
                result = res.one_or_none()
                if result:
                    return result.to_dc()
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_doc(self, doc_id: int) -> fullDoc | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    select(DocumentModel)
                    .where(DocumentModel.id == doc_id)
                    .options(selectinload(DocumentModel.owner))
                    .limit(1)
                )
                res = await session.scalars(query)
                result = res.one_or_none()
                if result:
                    return fullDoc(
                        id=result.id,
                        name=result.name,
                        last_edited=result.last_edited,
                        owner=UserforDoc(
                            id=result.owner.id, nickname=result.owner.nickname
                        ),
                    )
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_list_docs(self, user_id: int) -> List[fullDoc] | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    select(UserDocModel)
                    .where(UserDocModel.user_id == user_id)
                    .options(selectinload(UserDocModel.doc))
                    .options(selectinload(UserDocModel.user))
                )
                res = await session.scalars(query)
                results = res.all()
                if results:
                    return [
                        fullDoc(
                            id=result.doc.id,
                            name=result.doc.name,
                            last_edited=result.doc.last_edited,
                            owner=UserforDoc(
                                id=result.user.id, nickname=result.user.nickname
                            ),
                        )
                        for result in results
                    ]
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def update_doc(
        self, name: str, timestamp: datetime, doc_id: int
    ) -> bool | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    update(DocumentModel)
                    .where(DocumentModel.id == doc_id)
                    .values(name=name, last_edited=timestamp)
                )
                await session.execute(query)
                await session.commit()
                return True
        except sqlalchemy.exc.IntegrityError:
            return None

    async def delete_doc(self, doc_id: int) -> bool | None:
        try:
            async with self.app.database.session() as session:
                query = delete(DocumentModel).where(DocumentModel.id == doc_id)
                await session.execute(query)
                await session.commit()
                return True
        except sqlalchemy.exc.IntegrityError:
            return None

    async def add_user_to_doc(
        self, access: str, user_id: int, doc_id: int
    ) -> UserDocDC | None:
        try:
            async with self.app.database.session() as session:
                new_contributor = UserDocModel(
                    user_id=user_id, doc_id=doc_id, access=access
                )
                session.add(new_contributor)
                await session.commit()
                return new_contributor.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None

    async def update_user_access_to_doc(
        self, access: str, user_id: int, doc_id: int
    ) -> bool | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    update(UserDocModel)
                    .where(
                        (UserDocModel.doc_id == doc_id)
                        & (UserDocModel.user_id == user_id)
                    )
                    .values(access=access)
                )
                await session.execute(query)
                await session.commit()
                return True
        except sqlalchemy.exc.IntegrityError:
            return None

    async def remove_user_access(
        self, user_id: int, doc_id: int
    ) -> bool | None:
        try:
            async with self.app.database.session() as session:
                query = delete(UserDocModel).where(
                    (UserDocModel.doc_id == doc_id)
                    & (UserDocModel.user_id == user_id)
                )
                await session.execute(query)
                await session.commit()
                return True
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_user_access_to_doc(
        self, user_id: int, doc_id: int
    ) -> UserDocDC | None:
        try:

            async with self.app.database.session() as session:
                query = (
                    select(UserDocModel)
                    .where(
                        (UserDocModel.doc_id == doc_id)
                        & (UserDocModel.user_id == user_id)
                    )
                    .limit(1)
                )
                res = await session.scalars(query)
                result = res.one_or_none()
                if result:
                    return result.to_dc()
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_accesses_to_doc(self, doc_id: int) -> list[fullAccess] | None:
        try:

            async with self.app.database.session() as session:
                query = (
                    select(UserDocModel)
                    .where((UserDocModel.doc_id == doc_id))
                    .options(selectinload(UserDocModel.user))
                )
                res = await session.scalars(query)
                results = res.all()
                if results:
                    return [
                        fullAccess(
                            id=result.id,
                            doc_id=result.doc_id,
                            access=result.access,
                            user=UserforDoc(
                                id=result.user.id, nickname=result.user.nickname
                            ),
                        )
                        for result in results
                    ]
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None
