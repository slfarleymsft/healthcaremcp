FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make run.py executable
RUN chmod +x run.py

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "run.py", "--http"]