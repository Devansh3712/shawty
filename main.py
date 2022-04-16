from datetime import datetime

from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import status
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from shawty.database import Database
from shawty.routers.user import user
from shawty.utils.auth import auth_header


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user)
db = Database()


@app.get("/{hash}")
async def redirect(hash: str):
    if hash not in db.get_hashes():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link does not exist in database.",
        )
    url = db.get_url(hash)
    db.inc_visits(hash)
    return RedirectResponse(url)


@app.post("/new")
async def new_url(*, api_key: str = Depends(auth_header), request: Request, url: str):
    _hash = db.new_url(api_key, url)
    response = {"url": str(request.base_url) + _hash, "timestamp": datetime.utcnow()}
    return response
