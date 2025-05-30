from fastapi import FastAPI
from fastapi.responses import FileResponse
from mangum import Mangum
from db import DropboxDB, DropboxSettings
import dropbox
import datetime
import os
from zoneinfo import ZoneInfo  # Available in Python 3.9+
import random

from PIL import Image, ImageOps, ImageDraw, ImageFont

settings = DropboxSettings()  # type: ignore[call-arg]

app = FastAPI()

def convert_to_grayscale(input_path, output_path, target_size=(1072, 1448)):
    with Image.open(input_path) as img:
            # Convert to grayscale (8-bit)
            img = img.convert("L")
            # Crop bottom part that may or may not contain the stupid timestamp.
            width, height = img.size
            img = img.crop((0, 0, width, height - 465))
            # Flip 90.
            img = img.rotate(90, expand=True)
            # Resize while preserving aspect ratio and allowing upscale
            img = ImageOps.fit(img, target_size, method=Image.BICUBIC, centering=(0.5, 0.5))
            font = ImageFont.truetype("chb.otf", 30)
            # Write the battery level on the image.
            db = DropboxDB(settings.dropbox_refresh_token)
            level = db.get("battery")
            draw = ImageDraw.Draw(img)
            date_string = datetime.datetime.now(ZoneInfo("Europe/Paris")).strftime('%d.%m %H:%M:%S')
            text = f"BT: {level}% {date_string}"
            draw.text((10, 10), text, fill=(255,), font=font)
            # Save as PNG with 8-bit depth
            img.save(output_path, format="PNG", bits=8)

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

@app.get('/current_picture')
def current_picture():
    # Get all pictures in the folder.
    db = dropbox.Dropbox(oauth2_refresh_token = settings.dropbox_refresh_token, app_key = settings.dropbox_app_key, app_secret = settings.dropbox_app_secret)
    # List the files in the folder we have in settings plus "pics".
    path = f"{settings.dropbox_path}/pics"
    files = db.files_list_folder(path).entries
    # Take a random one.
    if not files:
        return {"error": "No pictures found"}
    # Choose a random file. But the same one every day. So day as random seed.
    today = datetime.date.today().isoformat()
    random.seed(today)
    file = random.choice(files)
    # Check if the file is a picture.
    if not isinstance(file, dropbox.files.FileMetadata):
        return {"error": "No picture found"}
    # Download the file. Unless its already cached here.
    # Save it to a temporary file.
    temp_file_path = f"/tmp/{file.name}"
    gray_temp_file_path = f"/tmp/gray_{file.name}"
    if not os.path.exists(temp_file_path):
        # Download the file.
        res = db.files_download(file.path_lower)
        with open(temp_file_path, "wb") as f:
            f.write(res.content)
    # Now convert it to grayscale.
    convert_to_grayscale(temp_file_path, gray_temp_file_path)
    # Return the grayscale image.
    return FileResponse(gray_temp_file_path, media_type="image/jpeg")

handler = Mangum(app)
