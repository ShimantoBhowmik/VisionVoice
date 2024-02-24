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