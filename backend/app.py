# app.py
from fastapi import FastAPI, File, UploadFile
from models import VideoToText, ImageToText, TextToSpeech, ScenesToText
from io import BytesIO
from fastapi.responses import StreamingResponse, Response
import PIL
import os
import hashlib
import soundfile as sf
import json
import base64
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


@app.get("/audios/{filename}")
async def get_audio(filename: str):
    data = b""
    with open(f"temp/{filename}", "rb") as f:
        data = f.read()

    return Response(data, media_type="audio/wav")

# image/live
@app.post("/image/live")
async def image_to_text_live(image: UploadFile = File(...)):
    # conver to PIL compatible format
    file = PIL.Image.open(image.file)
    text = i2t.get_text(file)
    print(text)
    audio = t2s.get_audio(text)
    # save np array to file as wav
    hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    sf.write(f"temp/{hash}.wav", audio["audio"], audio["sampling_rate"])
    print(text)
    # read audio in to base64 from file then delete file
    base64_audio = ""
    with open(f"temp/{hash}.wav", "rb") as f:
        base64_audio = base64.b64encode(f.read()).decode("utf-8")
    os.remove(f"temp/{hash}.wav")

    base64_audio = f"data:audio/wav;base64,{base64_audio}"

    return {"audio": base64_audio, "text": text}


# /visionsync
# Video
# text: bool
# audio: bool
# desc: bool
@app.post("/visionsync")
async def visionsync(
    text: bool | None,
    audio: bool | None,
    desc: bool | None,
    video: UploadFile = File(...),
    time_between_text: int = 10,
):
    # read text in output.txt
    # resp = ""
    # with open("output.txt", "r") as f:
    #     resp = f.read()
    # return Response(content=resp, media_type="application/json")

    text = not not text
    audio = not not audio
    desc = not not desc
    if not (text or audio or desc):
        return {"error": "Why are you even here?"}

    filename = await save_file(video)

    scenes = []

    def to_json(data):
        json_data = json.dumps(data) + "\n"
        return json_data.encode("utf-8")  # Encode JSON string to bytes


    def get_text():
        iterator = v2t.get_text(filename, time_between_text)
        for text in iterator:
            yield text

    def get_audio(text=None):
        text = text or i2t.get_text(filename)
        audio = t2s.get_audio(text)
        # save np array to file as wav
        hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        sf.write(f"temp/{hash}.wav", audio["audio"], audio["sampling_rate"])
        base64_audio = ""
        with open(f"temp/{hash}.wav", "rb") as f:
            base64_audio = base64.b64encode(f.read()).decode("utf-8")
        os.remove(f"temp/{hash}.wav")
        base64_audio = f"data:audio/wav;base64,{base64_audio}"
        return {"audio": base64_audio}

    def get_desc():
        return {"description": s2t.summarize(scenes)}

    def stream_response():
        for chunk in get_text():
            response = {}
            if text:
                response["text"] = chunk
            if audio:
                response["audio"] = get_audio(chunk["text"] if text else None)
            if desc:
                scenes.append(chunk["text"])
            if text or audio:
                yield to_json(response)
        yield to_json(get_desc())

    return StreamingResponse(
        stream_response(),
        media_type="application/json",
    )
