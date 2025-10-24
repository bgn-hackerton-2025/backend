# Virtual Environment Setup
python3 -m venv .venv
source .venv/bin/activate

# Gemini AI Image Analyzer

This project provides tools to analyze images using Google's Gemini AI model.

## Features

- 🖼️ Upload and analyze any image format (PNG, JPG, JPEG, GIF, BMP, WEBP)
- Providers can update their inventory with AI-generated insights

## Setup

### 1. Get Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key for use in the application

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:,,
```bash
pip install google-genai pillow streamlit
```

### 3. Set Environment Variable (Optional)

You can set your API key as an environment variable:
```bash
# On macOS/Linux
export GOOGLE_API_KEY="your-api-key-here"

# On Windows
set GOOGLE_API_KEY=your-api-key-here

```bash
# On macOS/Linux
export GOOGLE_API_KEY="your-api-key-here"

# On Windows
set GOOGLE_API_KEY=your-api-key-here
```

## Usage

### Web Interface (Recommended)

Run the Streamlit web application:

```bash
streamlit run image_analyzer.py
```

This will open a web browser where you can:
- Enter your API key
- Upload images via drag-and-drop
- View real-time analysis
- Use custom prompts
- Download analysis results

### Command Line Interface

For batch processing or integration into scripts:
