import re

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from shawty.api import api
from shawty.config import secrets
from shawty.database import Database


app = FastAPI()
app.include_router(api)
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
    regex = re.compile(
        r"^(?:http|ftp)s?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    if not (re.match(regex, data["url"]) is not None):
        return templates.TemplateResponse(
            "index.html", {"request": request, "error": "Invalid URL"}
        )
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


@app.get("/data/{hash}", response_class=HTMLResponse)
async def url_data(request: Request, hash: str):
    if hash not in db.get_hashes():
        return templates.TemplateResponse("404.html", {"request": request})
    data = db.get_url_data(hash)
    return templates.TemplateResponse(
        "data.html", {"request": request, "url_data": data.dict()}
    )
