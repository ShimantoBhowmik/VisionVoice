from fastapi import FastAPI, File, UploadFile
from models import VideoToText, ImageToText, TextToSpeech, ScenesToText
from io import BytesIO
from fastapi.responses import StreamingResponse
import PIL
import os
import hashlib
import json
from pathlib import Path

app = FastAPI()

v2t = VideoToText()
i2t = ImageToText()
t2s = TextToSpeech()
s2t = ScenesToText()


# disable cors
@app.middleware("http")
async def add_cors_header(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


# timing middleware
@app.middleware("http")
async def add_process_time_header(request, call_next):
    import time

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"Processing time: {process_time}")
    return response

#saving file video upload
async def save_file(file: UploadFile):
    data = file.file.read()
    file_hash = hashlib.sha256(data).hexdigest()
    print(file_hash)
    os.makedirs("./temp", exist_ok=True)
    filename = f"./temp/{file_hash}{Path(file.filename).suffix}"
    if os.path.exists(filename):
        print("File already exists")
        return filename
    with open(filename, "wb") as f:
        f.write(data)
    return filename

# /video
# Stream video to server
# returns stream of text
# req param dela
@app.post("/video/text")
async def video_to_text(
    video: UploadFile = File(...), time_between_text: int = 10
):
    filename = await save_file(video)

    def to_json(data):
        json_data = json.dumps(data) + "\n"
        return json_data.encode("utf-8")  # Encode JSON string to bytes

    def get_text():
        iterator = v2t.get_text(filename, time_between_text)
        for text in iterator:
            yield to_json(text)

    return StreamingResponse(
        get_text(),
        media_type="application/json",
    )


# /image
# Convert image to text
@app.post("/image/text")
async def image_to_text(image: UploadFile = File(...)):
    # conver to PIL compatible format
    file = PIL.Image.open(image.file)
    # downsample
    file = file.resize((640, 480))
    return {"text": i2t.get_text(file)}