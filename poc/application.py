import itertools
from typing import Annotated

from fastapi import FastAPI, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from .db import SessionDependency
from .models import Group, Grouping, Item, Sharing, User

app = FastAPI(debug=True)

##
## USERS
##


@app.post("/create_user")
async def create_user(
    email: Annotated[str, Form()],
    encryption_key: Annotated[str, Form()],
    session: SessionDependency,
):
    # create user
    u = User(email=email, encryption_key=encryption_key)
    session.add(u)
    await session.commit()
    await session.refresh(u)
    return u


@app.get("/get_user")
async def get_user(email: str, session: SessionDependency):
    # get user by id
    user = await session.execute(select(User).where(User.email == email).limit(1))
    try:
        return user.scalar_one()
    except Exception as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN) from None


@app.get("/get_users")
async def get_users(session: SessionDependency):
    # DEBUG ONLY
    user = await session.execute(select(User))
    return user.scalars().all()


##
## ITEMS
##


@app.post("/create_item")
async def create_item(
    owner_user_id: Annotated[int, Form()],
    encryption_key: Annotated[str, Form()],
    encryption_key_nonce: Annotated[str, Form()],
    content_nonce: Annotated[str, Form()],
    content: UploadFile,
    session: SessionDependency,
):
    # create item
    i = Item(content=await content.read(), content_nonce=content_nonce)
    session.add(i)
    await session.commit()

    # get private group
    # TODO distinguish between private group and regular hosted group
    result = await session.execute(
        select(Group.id).where(Group.host_user_id == owner_user_id).limit(1)
    )
    private_group_id = result.scalar_one()

    # create sharing between private group and new item
    session.add(
        Sharing(
            group_id=private_group_id,
            item_id=await i.awaitable_attrs.id,
            encryption_key=encryption_key,
            encryption_key_nonce=encryption_key_nonce,
        )
    )
    await session.commit()

    return await i.awaitable_attrs.id


@app.get("/get_items")
async def get_items(session: SessionDependency):
    # get all item ids
    result = await session.execute(select(Item))
    return [
        {"id": item.id, "content_nonce": item.content_nonce}
        for item in result.scalars().all()
    ]


@app.get("/view_item")
async def view_item(item_id: int, session: SessionDependency):
    # streaming return item content as bytes to avoid massive payloads
    item = await session.get(Item, item_id)

    def item_chunks():
        it = iter(item.content)
        for batch in iter(lambda: bytes(itertools.islice(it, 200)), b""):
            yield batch

    return StreamingResponse(item_chunks())


# class UpdateItemParams(BaseModel):
#     content: RawBytes


# @app.post("/update_item")
# async def update_item(params: UpdateItemParams): ...


##
## GROUPS
##


@app.post("/create_group")
async def create_group(
    host_user_id: Annotated[int, Form()],
    name: Annotated[str, Form()],
    encryption_key: Annotated[str, Form()],
    encryption_key_nonce: Annotated[str, Form()],
    session: SessionDependency,
):
    # create group
    g = Group(name=name, host_user_id=host_user_id)
    session.add(g)
    await session.commit()

    # create new grouping for private group
    session.add(
        Grouping(
            user_id=host_user_id,
            group_id=await g.awaitable_attrs.id,
            encryption_key=encryption_key,
            encryption_key_nonce=encryption_key_nonce,
        )
    )
    await session.commit()

    await session.refresh(g)
    return g


# @app.post("/invite_to_group")
# async def invite_to_group(
#     invitee_id: int,
#     group_id: int,
#     # invitee_encryption_key: RawBytes
#     encryption_key: RawBytes,
#     encryption_key_nonce: RawBytes,
#     session: SessionDependency,
# ):
#     # create new grouping. "status" (invite -> accept) not needed for POC
#     grouping = Grouping(
#         user_id=invitee_id,
#         group_id=group_id,
#         encryption_key=encryption_key,
#         encryption_key_nonce=encryption_key_nonce,
#     )
#     session.add(grouping)
#     await session.commit()
#     await session.refresh(grouping)
#     return grouping


# class RemoveFromGroupParams(BaseModel):
#     user_id: int
#     group_id: int


# @app.post("/remove_from_group")
# async def remove_from_group(params: RemoveFromGroupParams, session: SessionDependency):
#     # delete a grouping
#     await session.execute(
#         delete(Grouping).where(
#             Grouping.user_id == params.user_id, Grouping.group_id == params.group_id
#         )
#     )


@app.get("/get_memberships")
async def get_memberships(user_id: int, session: SessionDependency):
    # get groupings for a single user
    result = await session.execute(
        select(Grouping).where(Grouping.user_id == user_id).order_by(Grouping.group_id)
    )
    groupings = result.scalars().all()

    # get groups for the groupings
    result = await session.execute(
        select(Group)
        .where(Group.id.in_([grouping.group_id for grouping in groupings]))
        .order_by(Group.id)
    )
    groups = result.scalars().all()

    return [
        {"group": group, "grouping": grouping}
        for group, grouping in zip(groups, groupings, strict=True)
    ]


@app.get("/get_sharing")
async def get_sharing(item_id: int, group_id: int, session: SessionDependency):
    # get sharing for a single user and a single items
    sharing = await session.execute(
        select(Sharing)
        .where(Sharing.group_id == group_id, Sharing.item_id == item_id)
        .limit(1)
    )
    try:
        return sharing.scalar_one()
    except Exception:
        raise HTTPException(status.HTTP_403_FORBIDDEN) from None


# class ShareOrUnshareFromGroupParams(BaseModel):
#     new_user: int
#     group_id: int


# @app.post("/share_with_group")
# async def share_with_group(params: ShareOrUnshareFromGroupParams): ...


# @app.post("/unshare_with_group")
# async def unshare_with_group(params: ShareOrUnshareFromGroupParams): ...


app.mount("/", StaticFiles(directory="ui", html=True), name="static")
