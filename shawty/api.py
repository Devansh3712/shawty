from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from pydantic import EmailStr

from shawty.auth import auth_header
from shawty.database import Database

api = APIRouter(prefix="/api", tags=["shawty API"])
db = Database()


@api.post("/new")
async def new_url(*, api_key: str = Depends(auth_header), request: Request, url: str):
    _hash = db.new_url(api_key, url)
    response = {"url": str(request.base_url) + _hash, "timestamp": datetime.utcnow()}
    return response


@api.post("/user/new")
async def new_api_key(email: EmailStr):
    if email in db.get_emails():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email already registered with service.",
        )
    api_key: str = db.new_user(email)
    return {
        "data": f"{email} registered successfully.",
        "api_key": api_key,
        "timestamp": datetime.utcnow(),
    }


@api.get("/user/data")
async def get_user_data(api_key: str = Depends(auth_header)):
    user = db.get_user(api_key)
    urls = db.get_urls(api_key)
    result = {"email": user[0], "created": user[1], "urls": urls}
    return result
