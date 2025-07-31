#!/bin/bash

# Start the SQL Server container
echo "Starting SQL Server container..."
docker-compose up -d db

# Wait for SQL Server to be ready
echo "Waiting for SQL Server to be ready..."
sleep 30

# Run Django migrations
echo "Running Django migrations..."
python manage.py migrate

# Create superuser if needed
echo "Creating superuser..."
python manage.py createsuperuser --noinput || echo "Superuser already exists"

echo "Development setup complete!"
echo "You can now run: python manage.py runserver" 