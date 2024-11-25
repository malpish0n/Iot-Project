# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# If you have a certificate file for MQTT, copy it as well
# COPY cert.crt .

# Command to run the application
CMD ["python", "./python.py"]
