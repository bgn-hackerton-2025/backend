import google.generativeai as genai

genai.configure(api_key="AIzaSyCgXm5ZzJnuVavvchoYbxFRfPidsuMhFtY") # Use your actual API key here

# List all available models
for m in genai.list_models():
  print(f"Name: {m.name}")
  print(f"  Display Name: {m.display_name}")
  print(f"  Description: {m.description}")
  print(f"  Input Methods: {m.supported_generation_methods}")
  print("-" * 20)