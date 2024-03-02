import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

from bson import Binary
from bson.binary import UuidRepresentation

from bson.objectid import ObjectId
import utils

from auth.config import auth_config
from auth.exceptions import InvalidCredentials
from auth.schemas import AuthUser
from auth.security import check_password, hash_password
from database import Database  
async def create_user(user: AuthUser) -> Optional[dict[str, Any]]:
    user_data = {
        "email": user.email,
        "password": hash_password(user.password),
        "created_at": datetime.utcnow(),
    }
    result = await Database.db["auth_user"].insert_one(user_data)
    if result.inserted_id:
        user_data["_id"] = result.inserted_id
        return user_data
    return None

async def get_user_by_id(user_id: str) -> Optional[dict[str, Any]]:
    user = await Database.db["auth_user"].find_one({"_id": ObjectId(user_id)})
    return user

async def get_user_by_email(email: str) -> Optional[dict[str, Any]]:
    user = await Database.db["auth_user"].find_one({"email": email})
    return user

async def create_refresh_token(*, user_id: str, refresh_token: str = None) -> str:
    if not refresh_token:
        refresh_token = utils.generate_random_alphanum(64)
    token_data = {
        "uuid": Binary(uuid.uuid4().bytes, subtype=UuidRepresentation.STANDARD),
        "refresh_token": refresh_token,
        "expires_at": datetime.utcnow() + timedelta(seconds=auth_config.REFRESH_TOKEN_EXP),
        "user_id": user_id,
    }
    await Database.db["refresh_tokens"].insert_one(token_data)
    return refresh_token

async def get_refresh_token(refresh_token: str) -> Optional[dict[str, Any]]:
    token = await Database.db["refresh_tokens"].find_one({"refresh_token": refresh_token})
    return token

async def expire_refresh_token(refresh_token_uuid: uuid.UUID) -> None:
    await Database.db["refresh_tokens"].update_one(
        {"uuid": refresh_token_uuid},
        {"$set": {"expires_at": datetime.utcnow() - timedelta(days=1)}}
    )

async def authenticate_user(auth_data: AuthUser) -> dict[str, Any]:
    user = await get_user_by_email(auth_data.email)
    if not user:
        raise InvalidCredentials()
    if not check_password(auth_data.password, user["password"]):
        raise InvalidCredentials()
    return user
