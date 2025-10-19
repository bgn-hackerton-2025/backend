from google import genai
from PIL import Image
from io import BytesIO
import os, base64
import json
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from fastapi import File, UploadFile
from database.schemas import outfitGeneratorRequest

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

# Need 3 responses for 3 different outfit suggestions
responses = []
output = []

# prompt: str, image: Image.Image
def outfit_generator(requestBody: Optional[outfitGeneratorRequest], image_url: Optional[str] = None):
    # Generate content with both the text prompt and image input
    if not requestBody and not image:
        raise Exception("You must provide either a request body or an image.")
    
    prompt = requestBody.prompt
    contents = [prompt]
    image = None
    if image_url:
        image = Image.open(image_url)
        contents.append(image)


    for i in range(3):
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",  # must support image generation
            contents=contents,
            config={
                "system_instruction": [
                    """You are an outfit recommendation system for thrifted clothing.
                    Generate a complete outfit image that pairs well with the given item."""
                ]
            },
        )
        responses.append(response)

    for res in responses:
        for part in res.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                image = Image.open(BytesIO(part.inline_data.data))
                image.save("generated_image/generated_image.png")

                # Image as base64 encoding
                image_bytes = part.inline_data.data
                base64_str = base64.b64encode(image_bytes).decode("utf-8")
                print("Here's your outfit!")
                response = client.models.generate_content(model="gemini-2.5-flash", contents=["""for each item; trousers, shirt, jacket (if any) IN THE GIVEN IMAGE, 
                                              generate a simple description of each in JSON form:
                                              a description of what it is, its colour, style, brand, aesthetic like so:
                                              "[{\"trousers\": \"description\"},{\"jacket\": \"description\"}, {\"shirt\": \"description\"}]. 
                                              If a certain item is not in the picture, don't include it in your response.
                                              I only want keywords that I can then directly use in a full-text search of product descriptions.
                                              Do not give me full sentences or phrases or clauses. Just keywords. This is all
                                              I want in your response. generate the required JSON and nothing else. DON'T ADD ANY MARKDOWN FORMATTING. JUST RAW JSON that should be parseable by python json.loads.""", image])
                

                print(response)

                output.append({"image": base64_str, "description": json.loads(response.text)})

    if image_url and os.path.exists(image_url):
            try:
                os.remove(image_url)
                print(f"Cleaned up input image: {image_url}")
            except Exception as e:
                print(f"Error deleting input image: {str(e)}")

        
    return output