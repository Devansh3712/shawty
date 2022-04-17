from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security.api_key import APIKeyHeader
from fastapi.security.api_key import APIKeyQuery

from shawty.database import Database

db = Database()
API_KEY = APIKeyQuery(name="api_key")
X_API_KEY = APIKeyHeader(name="X-API-KEY")


def auth_header(x_api_key: str = Depends(X_API_KEY)):
    if x_api_key in db.get_keys():
        return x_api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key."
    )


def auth_query(api_key: str = Depends(API_KEY)):
    if api_key in db.get_keys():
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key."
    )
