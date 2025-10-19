from google import genai
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv
from outfit_generator import client


prompt = """
From the provided image, identify the shirt, jacket, and trousers.
For each item found, generate a JSON object with the following schema:
{
  "category": "The type of clothing (e.g., 'hat', 'shirt')",
  "subcategory": "A more specific type (e.g., 'beanie', 't-shirt'), optional",
  "color": "The primary color of the item",
  "style": "The general style (e.g., 'casual', 'formal')",
  "aesthetic": "The overall aesthetic (e.g., 'streetwear', 'vintage')"
}
Return a JSON object containing a list called "clothing_items". If an item is not visible, do not include it in the list.
"""


def jsonify_image(image_url: str):

    image = Image.open(image_url)


    client.models.generate_content(
        model="gemini-2.5-pro",
        contents=[prompt, image]

    )



