from google import genai
import PIL.Image
import io

client = genai.Client(api_key="AIzaSyCgXm5ZzJnuVavvchoYbxFRfPidsuMhFtY")

# Make sure you have an image file (e.g., 'shirt.jpg') in the same directory
img = PIL.Image.open('imgs/carhartt--jacket.png')

def outfit_generator(prompt: str, image: PIL.Image.Image): 
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
        generation_config={
            "response_mime_type": "image/png"
        }
    )

    # The response should contain binary image data
    image_data = response.generated_content[0].data
    outfit_image = PIL.Image.open(io.BytesIO(image_data))
    outfit_image.save("outfit.png")
    outfit_image.show()
    print("✅ Outfit image generated and saved as outfit.png")

# Example call
outfit_generator("Generate a trendy thrifted outfit to match this jacket.", img)
