from google import genai
import PIL.Image
import types

client = genai.Client(api_key="AIzaSyCgXm5ZzJnuVavvchoYbxFRfPidsuMhFtY")

# Make sure you have an image file (e.g., 'shirt.jpg') in the same directory
img = PIL.Image.open('imgs/carhartt--jacket.png')


def outfit_generator(contents: str): 
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        # The system_instruction provides context for the model's behavior
        config={
                "system_instruction":
                    ["""You are an outfit recommendation system for thrifted clothing.
                You will be given some type of user input from any combination of image input
                (of a piece of clothing), hand written sketches (of a piece of clothing),
                or natural language input describing an outfit of a particular style the user has in mind.
                Your task is to generate an outfit for them based on these inputs."""
                    ]
        },
        # The contents should be a list containing the user's prompt and images
        contents=[contents, img]
    )

    print(response.text)