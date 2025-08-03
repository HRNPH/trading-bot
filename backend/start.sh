#!/bin/bash

# Add src/ directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/../src"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate Prisma client
prisma generate

# Run database migrations
alembic upgrade head

# Start the application
python main.py 