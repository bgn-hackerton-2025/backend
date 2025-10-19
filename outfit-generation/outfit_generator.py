from google import genai
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
client = genai.Client(api_key=api_key)

# Make sure you have an image file (e.g., 'shirt.jpg') in the same directory
img = Image.open('imgs/carhartt-jacket-2.png')

def outfit_generator(prompt: str, image: Image.Image): 
    # Generate content with both the text prompt and image input
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





# Example call
outfit_generator("Generate a trendy thrifted outfit to match this jacket.", img)
