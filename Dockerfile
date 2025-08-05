# Use an official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Avoid Python stdout buffering (for real-time logs)
ENV PYTHONUNBUFFERED=1

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application and related files
COPY app.py .
COPY scripts/ ./scripts/
COPY xml/ ./xml/

# Expose port used by Gunicorn
EXPOSE 5000

# Run the app using Gunicorn (production WSGI server)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app", "--log-level", "info", "--access-logfile", "-"]
