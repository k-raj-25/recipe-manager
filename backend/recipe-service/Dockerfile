# User Service Dockerfile
FROM python:3.11.1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy code
COPY . .

# Run the user service
CMD ["python", "run.py"]
