from fastapi import FastAPI
from mangum import Mangum
from db import DropboxDB, DropboxSettings
settings = DropboxSettings()  # type: ignore[call-arg]

app = FastAPI()

@app.get("/")
def hello_world() -> dict[str, str]:
    return {'message': 'Hello from FastAPI'}

@app.get("/battery")
def battery() -> dict[str, str]:
    db = DropboxDB(settings.dropbox_refresh_token)
    value: str = db.get("battery")
    return {"battery": value + "%"}

@app.post("/battery")
def battery_post(level: int) -> dict[str, str]:
    db = DropboxDB(settings.dropbox_refresh_token)
    db.set("battery", str(level))
    return battery()

handler = Mangum(app)
