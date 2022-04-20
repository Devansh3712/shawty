import re
from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from pydantic import EmailStr

from shawty.auth import auth_header
from shawty.database import Database
from shawty.schema import Shawty

api = APIRouter(prefix="/api", tags=["shawty API"])
db = Database()


@api.get("/")
async def root():
    return {"data": "shawty API is working.", "Source code": "https://github.com/Devansh3712/shawty", "timestamp": datetime.now()}


@api.post("/new")
async def new_url(*, api_key: str = Depends(auth_header), request: Request, url: str):
    regex = re.compile(
        r"^(?:http|ftp)s?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    if not (re.match(regex, url) is not None):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid URL."
        )
    _hash = db.new_url(api_key, url)
    response = {"url": str(request.base_url) + _hash, "timestamp": datetime.utcnow()}
    return response


@api.get("/data/{hash}", response_model=Shawty)
async def url_data(*, api_key: str = Depends(auth_header), request: Request, hash: str):
    if hash not in db.get_hashes():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hash not found in database."
        )
    data = db.get_url_data(hash)
    return data


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
