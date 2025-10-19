from google import genai
from PIL import Image
from io import BytesIO
import os, base64
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from fastapi import File, UploadFile
from database.schemas import outfitGeneratorRequest

load_dotenv()
api_key = os.getenv("API_KEY")
client = genai.Client(api_key=api_key)

# Make sure you have an image file (e.g., 'shirt.jpg') in the same directory
img = Image.open('imgs/carhartt-jacket-2.png')
# Need 3 responses for 3 different outfit suggestions
responses = []

# prompt: str, image: Image.Image
def outfit_generator(requestBody: outfitGeneratorRequest, image: Optional[UploadFile] = File(None)):
    # Generate content with both the text prompt and image input
    prompt: str = ""
    image = ""

    if not requestBody and not image:
        raise Exception("You must provide either a request body or an image.")
    
    if requestBody and requestBody.prompt:
        prompt = requestBody.prompt

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",  # must support image generation
        contents=[prompt, image],
        config={
            "system_instruction": [
                """You are an outfit recommendation system for thrifted clothing.
                Generate a complete outfit image that pairs well with the given item."""
            ]
        },
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            image.save("generated_image/generated_image.png")

            # Image as base64 encoding
            image_bytes = part.inline_data.data
            base64_str = base64.b64encode(image_bytes).decode("utf-8")
            print("Here's your outfit!")
            return base64_str
        

