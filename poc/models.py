from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    """User model"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(index=True, primary_key=True, autoincrement=True)
    public_encryption_key: Mapped[bytes]


class Group(Base):
    """Group model"""

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(index=True, primary_key=True, autoincrement=True)


class Item(Base):
    """Item model"""

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(index=True, primary_key=True, autoincrement=True)


class Grouping(Base):
    """Grouping model: a connection between a user and a group (membership)"""

    __tablename__ = "groupings"

    id: Mapped[int] = mapped_column(index=True, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))


class Sharing(Base):
    """Sharing model: a connection between an item and a user (permission)"""

    __tablename__ = "sharings"

    id: Mapped[int] = mapped_column(index=True, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
