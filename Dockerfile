FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY templates/ ./templates/
COPY static/ ./static/

# Expose the Flask application port
EXPOSE 5000

# Start the application
CMD ["python", "app.py"]
