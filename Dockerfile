# 1. Use an official Python runtime as a parent image
FROM python:3.11-slim

# 2. Set the working directory in the container
WORKDIR /app

# 3. Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the application code into the container
COPY . .

# 5. Expose the port the app runs on
EXPOSE 8080

# 6. Start the application
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}