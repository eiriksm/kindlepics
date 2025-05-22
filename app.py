from fastapi import FastAPI
from mangum import Mangum
from db import DropboxDB, DropboxSettings
settings = DropboxSettings()  # type: ignore[call-arg]

app = FastAPI()

@app.get("/")
def hello_world():
    return {'message': 'Hello from FastAPI'}


@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f'Hello from FastAPI, {name}!'}

@app.get("/battery")
def battery():
    db = DropboxDB(settings.dropbox_refresh_token)
    value: str = db.get("battery")
    return {"battery": value + "%"}

@app.post("/battery")
def battery_post(level: int):
    db = DropboxDB(settings.dropbox_refresh_token)
    value: str = db.set("battery", str(level))
    return battery()

handler = Mangum(app)
