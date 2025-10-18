# 1. Use an official Python runtime as a parent image
FROM python:3.11-slim

# 2. Set the working directory in the container
WORKDIR /app

# 3. Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the application code into the container
COPY . .

# 5. Set build-time environment variables for migration
# These will be overridden by runtime environment variables
ARG DATABASE_URL
ENV DATABASE_URL=${DATABASE_URL}

# 6. Run database migrations during build
RUN if [ -n "$DATABASE_URL" ]; then \
        echo "Running database migrations during build..." && \
        python -m alembic upgrade head; \
    else \
        echo "DATABASE_URL not provided, skipping migrations during build"; \
    fi

# 7. Expose the port the app runs on
EXPOSE 8080

# 8. Start the application directly (no migrations at runtime)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}