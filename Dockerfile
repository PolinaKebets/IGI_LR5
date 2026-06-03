FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Run migrations, load data, and start gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && if [ -f fixtures/initial_data.json ]; then python manage.py load_data || python manage.py seed_data; else python manage.py seed_data; fi && gunicorn --bind 0.0.0.0:8000 chemshop.wsgi:application"]
