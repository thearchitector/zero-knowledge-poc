from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class Base(DeclarativeBase, MappedAsDataclass, AsyncAttrs):
    pass


class User(Base):
    """User model"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    email: Mapped[str] = mapped_column(index=True)
    encryption_key: Mapped[str]  # user's public key
    encryption_key_salt: Mapped[str]  # salt used to gen key pair


class Group(Base):
    """Group model"""

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str]
    host_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )  # the host of the group. a couple interesting things we can do here. either leave it nullable, so the built-in World/Community groups are owned by nobody, or ALSO have a built-in goddess user
    private: Mapped[bool]


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
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), index=True)
    encryption_key: Mapped[
        str
    ]  # group's symmetric key encrypted with user's public key


class Sharing(Base):
    """Sharing model: a connection between an item and a group (permission)"""

    __tablename__ = "sharings"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    encryption_key: Mapped[
        str
    ]  # item's symmetric key encrypted with groups's symmetric key
    encryption_key_nonce: Mapped[str]  # random value used for key encryption
