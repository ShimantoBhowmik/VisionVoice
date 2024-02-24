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