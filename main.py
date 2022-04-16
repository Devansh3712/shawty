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

from shawty.config import secrets
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
