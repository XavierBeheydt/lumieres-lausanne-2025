# syntax=docker/dockerfile:1

# 1. Use a Specific Python Version for Consistency
FROM python:3.11-slim

# 2. Set Environment Variables
# - PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disk
# - PYTHONUNBUFFERED: Ensures output is sent straight to the terminal without buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set Working Directory
WORKDIR /app

# 4. Install System Dependencies
# - Install only necessary packages to minimize image size
# - Use --no-install-recommends to avoid unnecessary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 5. Upgrade pip and Install Python Dependencies
# - Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 6. Copy Project Files
# - Copy the entire project after dependencies are installed
COPY . .

# 7. Create a Non-Root User for Security
RUN adduser --disabled-password --no-create-home appuser

# 8. Change Ownership of the Application Files
# - Ensure the non-root user has access to the project files
RUN chown -R appuser:appuser /app

# 9. Switch to the Non-Root User
USER appuser

# 10. Collect Static Files
# - Pre-collect static files to reduce runtime overhead
# RUN python manage.py collectstatic --noinput

# 11. Expose the Application Port
# - Inform Docker that the container listens on port 8000 at runtime
EXPOSE 8000

# 12. Start the Application Using Gunicorn
# - Gunicorn is a production-ready WSGI server
CMD ["gunicorn", "lumieres.wsgi:application", "--bind", "0.0.0.0:8000"]
