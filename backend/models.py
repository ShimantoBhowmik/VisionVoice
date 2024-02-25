from PIL import Image
from datasets import load_dataset
import torch
import google.generativeai as genai
import cv2
from transformers import pipeline


class ImageToText:
    def __init__(self):
        self.pipe = pipeline(
            "image-to-text", model="Salesforce/blip-image-captioning-large",
            device=0
        )

    def remove_araf(self, text):
        text = text.split()
        return " ".join(filter(lambda x: "araf" not in x , text))

    def get_text(self, image_path):
        gen = self.pipe(image_path)
        return str.join("\n", (self.remove_araf(x["generated_text"]) for x in gen))


class TextToSpeech:
    def __init__(self):
        self.pipe = pipeline("text-to-audio", model="microsoft/speecht5_tts", device=0)
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
            msec = int(cap.get(cv2.CAP_PROP_POS_MSEC))

            # time = 00h:00m:00s
            time = f"{msec // 3600000:02}h:{(msec // 60000) % 60:02}m:{(msec // 1000) % 60:02}s"

            # remove leading 00s
            time = time.replace("00h:", "").replace("00m:", "")
            
            yield {
                "text": self.i2t.get_text(pil_image),
                # as string
                "time": time
            }
            frames_to_skip += 1
        cap.release()


class ScenesToText:
    # "scenes" = Text description of each scene

    def __init__(self):
        self.summarization_prompt = """
Describe the scene depicted in the paragraph below using narrative style. Avoid directly quoting the original text and refrain from using the word 'image.' Begin with 'The video portrays...' Maintain a narrative tone, avoiding the use of first-person pronouns. Minimize comma usage. Limit your response to 100 words
        """.strip()
        genai.configure(api_key=self.API_KEY)
        self.model = genai.GenerativeModel("gemini-pro")

    def summarize(self, scenes: str | list[str]):
        if isinstance(scenes, list):
            scenes = "\n".join(scenes)

        print(self.summarization_prompt + "\n\n" + scenes + "\n\n" + "The summary is:")

        result = genai.generate_text(
            prompt=self.summarization_prompt + "\n\n" + scenes,
        ).result
        print(result)

        return result
