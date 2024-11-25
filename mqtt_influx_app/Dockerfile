# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables to avoid Python buffering
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Copy the CA certificate if needed (optional)
# COPY cert.crt .

# Specify the command to run your app
CMD ["python", "pyton.py"]

# Expose any ports if needed (optional, adjust based on your app)
# EXPOSE 8883  # For MQTT
