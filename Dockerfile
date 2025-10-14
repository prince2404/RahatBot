# Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Update sqlite3
RUN apt-get update && \
    apt-get install -y --no-install-recommends sqlite3 libsqlite3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Verify sqlite3 version (optional)
RUN sqlite3 --version


# Copy the project files into the container
COPY . .

# Install any dependencies specified in requirements.txt
# If you don't have a requirements.txt, create one using: pip freeze > requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Uvicorn will listen on (default is 8000)
EXPOSE 8000

# Set environment variables (if needed - load from .env during runtime)
# ENV OPENAI_API_KEY=your_openai_api_key  # Not recommended to hardcode, use .env

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
