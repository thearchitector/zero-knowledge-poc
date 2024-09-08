from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class Base(DeclarativeBase, MappedAsDataclass, AsyncAttrs):
    pass


class User(Base):
    """User model"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    email: Mapped[str]
    encryption_key: Mapped[str]  # user's public key


class Group(Base):
    """Group model"""

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str]
    host_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))


class Item(Base):
    """Item model"""

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    content: Mapped[bytes]  # content encrypted with a symmetric encryption key
    content_nonce: Mapped[str]  # random value used for content encryption


class Grouping(Base):
    """Grouping model: a connection between a user and a group (membership)"""

    __tablename__ = "groupings"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    encryption_key: Mapped[
        str
    ]  # group's symmetric key encrypted with user's public key
    encryption_key_nonce: Mapped[str]  # random value used for key encryption


class Sharing(Base):
    """Sharing model: a connection between an item and a group (permission)"""

    __tablename__ = "sharings"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    encryption_key: Mapped[
        str
    ]  # item's symmetric key encrypted with groups's symmetric key
    encryption_key_nonce: Mapped[str]  # random value used for key encryption
