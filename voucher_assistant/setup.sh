#!/bin/bash

# OneU Voucher Assistant Setup Script
echo "=== OneU AI Voucher Assistant Setup ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env file from example..."
    cp .env.example .env
    print_warning "Please edit .env file with your configuration before running the application"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p data/elasticsearch
mkdir -p config
mkdir -p logs

# Set proper permissions for Elasticsearch
print_status "Setting permissions for Elasticsearch data directory..."
chmod 777 data/elasticsearch

# Build and start services
print_status "Building and starting services with Docker Compose..."
docker-compose up --build -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# Check if Elasticsearch is ready
print_status "Checking Elasticsearch health..."
for i in {1..30}; do
    if curl -s http://localhost:9200/_cluster/health > /dev/null; then
        print_status "Elasticsearch is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Elasticsearch failed to start within timeout"
        exit 1
    fi
    echo "Waiting for Elasticsearch... ($i/30)"
    sleep 2
done

# Setup knowledge base
print_status "Setting up knowledge base..."
cd data_processing
python setup_knowledge_base.py
cd ..

# Check backend health
print_status "Checking backend health..."
for i in {1..15}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        print_status "Backend is ready!"
        break
    fi
    if [ $i -eq 15 ]; then
        print_error "Backend failed to start within timeout"
        exit 1
    fi
    echo "Waiting for backend... ($i/15)"
    sleep 2
done

# Check frontend
print_status "Checking frontend..."
for i in {1..15}; do
    if curl -s http://localhost:3000 > /dev/null; then
        print_status "Frontend is ready!"
        break
    fi
    if [ $i -eq 15 ]; then
        print_error "Frontend failed to start within timeout"
        exit 1
    fi
    echo "Waiting for frontend... ($i/15)"
    sleep 2
done

print_status "=== Setup Complete! ==="
echo ""
echo "🚀 OneU AI Voucher Assistant is now running!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 Elasticsearch: http://localhost:9200"
echo ""
echo "📋 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop all services:"
echo "   docker-compose down"
echo ""
echo "📝 Don't forget to:"
echo "   1. Configure your Google Cloud credentials in config/"
echo "   2. Update the .env file with your settings"
echo "   3. Add your voucher data to data/ directory"
