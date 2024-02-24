from PIL import Image
from datasets import load_dataset
import torch
import google.generativeai as genai
import cv2
from transformers import pipeline


class ImageToText:
    def __init__(self):
        self.pipe = pipeline(
            "image-to-text", model="Salesforce/blip-image-captioning-large"
        )

    def get_text(self, image_path):
        gen = self.pipe(image_path)
        return str.join("\n", (x["generated_text"] for x in gen))


class TextToSpeech:
    def __init__(self):
        self.pipe = pipeline("text-to-audio", model="microsoft/speecht5_tts")
        embeddings_dataset = load_dataset(
            "Matthijs/cmu-arctic-xvectors", split="validation"
        )
        self.speaker_embedding = torch.tensor(
            embeddings_dataset[7306]["xvector"]
        ).unsqueeze(0)

    def get_audio(self, text):
        return self.pipe(
            text,
            forward_params={"speaker_embeddings": self.speaker_embedding},
        )


class VideoToText:
    def __init__(self):
        self.i2t = ImageToText()

    def get_text(self, video_path, time_between_text=10):
        cap = cv2.VideoCapture(video_path)
        # set to read text_per_second frames per second
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(fps)
        frames_to_skip = 0
        while cap.isOpened():
            if frames_to_skip == 0:
                frames_to_skip = int(time_between_text * fps)
            else:
                frames_to_skip -= 1
                cap.grab()
                continue

            ret, frame = cap.read()
            if not ret:
                break

            # convert frame to pil image
            pil_image = Image.fromarray(frame)

            yield {
                "text": self.i2t.get_text(pil_image),
                "time": int(cap.get(cv2.CAP_PROP_POS_MSEC)),
            }
            frames_to_skip += 1
        cap.release()


class ScenesToText:
    # "scenes" = Text description of each scene

    def __init__(self):
        self.API_KEY = "AIzaSyDM7F4Ui1Utj7dN3EkV6h-cGj0sfTRNYzQ"
        self.summarization_prompt = """
        Summarize this scene as a narrative style paragraph where the time key is for which frame (video at 24fps) and text is what was at that frame. Do not just repeat text from the original description. 

            Max Length: 100 words
        """.strip()
        genai.configure(api_key=self.API_KEY)
        self.model = genai.GenerativeModel("gemini-pro")

    def summarize(self, scenes: str | list[str]):
        if isinstance(scenes, list):
            scenes = "\n".join(scenes)

        result = genai.generate_text(
            prompt=self.summarization_prompt + "\n\n" + scenes,
        ).result
        print(result)

        return result
