import itertools
from contextlib import asynccontextmanager
from os import scandir
from typing import Annotated

from fastapi import FastAPI, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import delete, func, select

from .db import SessionDependency, create_session
from .models import Group, Grouping, Item, Sharing, User

WORLD_GROUP_ID: int = 1


@asynccontextmanager
async def create_default_groups(_: FastAPI):
    # DEBUG ONLY
    # ensure that the first group that exits in the application is World
    async with create_session() as session:
        group: Group | None = await session.get(Group, WORLD_GROUP_ID)
        if not group:
            session.add(Group(host_user_id=None, name="World", private=False))
            await session.commit()

    yield


app = FastAPI(lifespan=create_default_groups, debug=True)

EncodedBytes = Annotated[str, Form()]

##
## USERS
##


#### create
@app.post("/create_user")
async def create_user(
    email: Annotated[str, Form()],
    encryption_key: EncodedBytes,
    encryption_key_salt: EncodedBytes,
    session: SessionDependency,
):
    # create user
    u = User(
        email=email,
        encryption_key=encryption_key,
        encryption_key_salt=encryption_key_salt,
    )
    session.add(u)
    await session.commit()
    await session.refresh(u)
    return u


#### read
@app.get("/get_user")
async def get_user(email: str, session: SessionDependency):
    # get user by id
    user = await session.execute(select(User).where(User.email == email).limit(1))
    try:
        return user.scalar_one()
    except Exception as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN) from None


#### read
@app.get("/get_users")
async def get_users(session: SessionDependency):
    # DEBUG ONLY
    user = await session.execute(select(User))
    return user.scalars().all()


##
## ITEMS
##


#### create
@app.post("/create_item")
async def create_item(
    owner_user_id: Annotated[int, Form()],
    encryption_key: EncodedBytes,
    encryption_key_nonce: EncodedBytes,
    content_nonce: EncodedBytes,
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


#### read
@app.get("/get_items")
async def get_items(session: SessionDependency):
    # get all item ids
    result = await session.execute(select(Item))
    return [
        {"id": item.id, "content_nonce": item.content_nonce}
        for item in result.scalars().all()
    ]


#### read
@app.get("/get_item")
async def get_item(item_id: int, session: SessionDependency):
    # get item by id
    item = await session.get(Item, item_id)
    return {"id": item.id, "content_nonce": item.content_nonce}


#### read
@app.get("/view_item")
async def view_item(item_id: int, session: SessionDependency):
    # streaming return item content as bytes to avoid massive payloads
    item = await session.get(Item, item_id)

    def item_chunks():
        it = iter(item.content)
        for batch in iter(lambda: bytes(itertools.islice(it, 200)), b""):
            yield batch

    return StreamingResponse(item_chunks())


@app.patch("/update_item")
async def update_item(
    item_id: Annotated[int, Form()],
    content_nonce: EncodedBytes,
    content: UploadFile,
    session: SessionDependency,
):
    item = await session.get(Item, item_id)
    item.content = await content.read()
    item.content_nonce = content_nonce
    session.add(item)
    await session.commit()


##
## GROUPS
##


@app.post("/create_group")
async def create_group(
    host_user_id: Annotated[int, Form()],
    name: Annotated[str, Form()],
    grouping_encryption_key: EncodedBytes,
    session: SessionDependency,
):
    num_existing: int = (
        await session.execute(
            select(func.count()).where(Group.host_user_id == host_user_id)
        )
    ).scalar_one()

    # create group
    g = Group(name=name, host_user_id=host_user_id, private=(num_existing == 0))
    session.add(g)
    await session.commit()

    # create new grouping for private group
    session.add(
        Grouping(
            user_id=host_user_id,
            group_id=await g.awaitable_attrs.id,
            encryption_key=grouping_encryption_key,
        )
    )
    await session.commit()

    await session.refresh(g)
    return g


### GROUPINGS


#### create
@app.post("/invite_to_group")
async def invite_to_group(
    invitee_id: Annotated[int, Form()],
    group_id: Annotated[int, Form()],
    grouping_encryption_key: EncodedBytes,
    session: SessionDependency,
):
    # create new grouping. "status" (invite -> accept) not needed for POC
    grouping = Grouping(
        user_id=invitee_id, group_id=group_id, encryption_key=grouping_encryption_key
    )
    session.add(grouping)
    await session.commit()
    await session.refresh(grouping)
    return grouping


#### read
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


class GetGroupingsParams(BaseModel):
    user_id: int
    group_ids: list[int]


#### read
@app.post("/get_groupings")
async def get_groupings(params: GetGroupingsParams, session: SessionDependency):
    # get all groupings for a single user against the known groups
    groupings = await session.execute(
        select(Grouping).where(
            Grouping.user_id == params.user_id, Grouping.group_id.in_(params.group_ids)
        )
    )
    ## ideally we'd ensure len(groupings) == len(group_ids) for security
    return {grouping.group_id: grouping for grouping in groupings.scalars().all()}


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

### SHARINGS


#### create
@app.post("/share_with_group")
async def share_with_group(
    item_id: Annotated[int, Form()],
    group_id: Annotated[int, Form()],
    encryption_key: EncodedBytes,
    encryption_key_nonce: EncodedBytes,
    session: SessionDependency,
):
    session.add(
        Sharing(
            item_id=item_id,
            group_id=group_id,
            encryption_key=encryption_key,
            encryption_key_nonce=encryption_key_nonce,
        )
    )
    await session.commit()


#### read
@app.get("/get_sharings")
async def get_sharings(item_id: int, session: SessionDependency):
    # get all sharings for a single item.
    sharing = await session.execute(select(Sharing).where(Sharing.item_id == item_id))
    return sharing.scalars().all()


#### read
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


#### update
@app.patch("/update_sharing")
async def update_sharing(
    item_id: Annotated[int, Form()],
    group_id: Annotated[int, Form()],
    encryption_key: EncodedBytes,
    encryption_key_nonce: EncodedBytes,
    session: SessionDependency,
):
    # get all sharings for a single item.
    sharing = await session.execute(
        select(Sharing).where(Sharing.item_id == item_id, Sharing.group_id == group_id)
    )
    sharing = sharing.scalar_one()
    sharing.encryption_key = encryption_key
    sharing.encryption_key_nonce = encryption_key_nonce
    session.add(sharing)
    await session.commit()


class UnshareFromGroupParams(BaseModel):
    item_id: int
    group_id: int


#### delete
@app.delete("/unshare_from_group")
async def unshare_from_group(
    params: UnshareFromGroupParams, session: SessionDependency
):
    # delete the sharing between the item and the group
    await session.execute(
        delete(Sharing).where(
            Sharing.item_id == params.item_id, Sharing.group_id == params.group_id
        )
    )
    await session.commit()


app.mount("/", StaticFiles(directory="ui", html=True), name="static")
