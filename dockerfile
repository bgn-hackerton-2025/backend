# 1. Use an official Python runtime as a parent image
FROM python:3.11-slim

# 2. Set the working directory in the container
WORKDIR /app

# 3. Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the application code into the container
COPY . .

# 5. Expose the port the app runs on (this is for documentation)
# The PORT env var will be set by Cloud Run at runtime.
EXPOSE 8080

# 6. Define the command to run your app using uvicorn
# We use the PORT environment variable provided by Cloud Run.
# The host '0.0.0.0' is crucial to accept connections from outside the container.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]