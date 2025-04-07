# Use Python 3.11 slim as the base image.
FROM python:3.11-slim

# Set the working directory.
WORKDIR /app

# Copy your requirements file if needed.
COPY requirements.txt .

# Install Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the BACnet simulator script into the image.
COPY device-sim.py .

# Default command to run your simulator.
CMD ["python", "device-sim.py"]
