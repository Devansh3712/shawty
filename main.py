from datetime import datetime

from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr

from shawty.auth import auth_header
from shawty.config import secrets
from shawty.database import Database


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
db = Database()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def short_url(request: Request):
    data = await request.form()
    _hash = db.new_url(secrets.API_KEY, data["url"])
    return templates.TemplateResponse(
        "index.html", {"request": request, "short_url": str(request.base_url) + _hash}
    )


@app.get("/{hash}")
async def redirect(request: Request, hash: str):
    if hash not in db.get_hashes():
        return templates.TemplateResponse("404.html", {"request": request})
    url = db.get_url(hash)
    db.inc_visits(hash)
    return RedirectResponse(url)


@app.post("/api/new")
async def new_url(*, api_key: str = Depends(auth_header), request: Request, url: str):
    _hash = db.new_url(api_key, url)
    response = {"url": str(request.base_url) + _hash, "timestamp": datetime.utcnow()}
    return response


@app.post("/api/user/new")
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


@app.get("/api/user/data")
async def get_user_data(api_key: str = Depends(auth_header)):
    user = db.get_user(api_key)
    urls = db.get_urls(api_key)
    result = {"email": user[0], "created": user[1], "urls": urls}
    return result
