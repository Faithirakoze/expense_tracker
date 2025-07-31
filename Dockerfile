# Use lightweight Python 3.11 image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app code into the container
COPY . .

# Expose port 5000
EXPOSE 5000

# Tell Docker how to run your app
CMD ["python", "main.py"]
