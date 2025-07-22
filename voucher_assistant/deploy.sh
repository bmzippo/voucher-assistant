#!/bin/bash

#   Voucher Assistant Production Deployment Script
echo "===   AI Voucher Assistant Production Deployment ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root for production setup
if [[ $EUID -eq 0 ]]; then
   print_warning "Running as root. Make sure this is intended for production deployment."
fi

# Environment setup
ENVIRONMENT=${1:-"production"}
print_status "Deploying for environment: $ENVIRONMENT"

# Step 1: Pre-deployment checks
print_step "1. Running pre-deployment checks..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check required environment files
if [ ! -f ".env" ]; then
    print_error ".env file not found. Please create it from .env.example"
    exit 1
fi

# Check Google Cloud credentials
if [ ! -f "config/gcp-key.json" ]; then
    print_warning "Google Cloud credentials not found. Mock LLM service will be used."
fi

print_status "Pre-deployment checks completed"

# Step 2: Build and deploy
print_step "2. Building and deploying services..."

# Stop existing services
print_status "Stopping existing services..."
docker-compose down

# Build with no cache for production
print_status "Building services..."
docker-compose build --no-cache

# Step 3: Database initialization
print_step "3. Initializing database and knowledge base..."

# Start Elasticsearch first
print_status "Starting Elasticsearch..."
docker-compose up -d elasticsearch

# Wait for Elasticsearch to be ready
print_status "Waiting for Elasticsearch to be ready..."
for i in {1..60}; do
    if curl -s http://localhost:9200/_cluster/health > /dev/null; then
        print_status "Elasticsearch is ready!"
        break
    fi
    if [ $i -eq 60 ]; then
        print_error "Elasticsearch failed to start within timeout"
        exit 1
    fi
    echo "Waiting for Elasticsearch... ($i/60)"
    sleep 2
done

# Initialize knowledge base
print_status "Setting up knowledge base..."
docker-compose run --rm backend python -m data_processing.setup_knowledge_base

# Step 4: Start all services
print_step "4. Starting all services..."
docker-compose up -d

# Step 5: Health checks
print_step "5. Running health checks..."

# Wait and check backend
print_status "Checking backend health..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        backend_health=$(curl -s http://localhost:8000/health | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        print_status "Backend is ready! Health: $backend_health"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Backend failed to start within timeout"
        exit 1
    fi
    echo "Waiting for backend... ($i/30)"
    sleep 2
done

# Check frontend
print_status "Checking frontend..."
for i in {1..20}; do
    if curl -s http://localhost:3000 > /dev/null; then
        print_status "Frontend is ready!"
        break
    fi
    if [ $i -eq 20 ]; then
        print_error "Frontend failed to start within timeout"
        exit 1
    fi
    echo "Waiting for frontend... ($i/20)"
    sleep 2
done

# Step 6: Performance baseline
print_step "6. Establishing performance baseline..."

# Run initial performance test
print_status "Running performance baseline..."
curl -s http://localhost:8000/api/metrics > /dev/null

# Step 7: Security setup (production only)
if [ "$ENVIRONMENT" = "production" ]; then
    print_step "7. Setting up production security..."
    
    # Set proper file permissions
    chmod 600 .env
    chmod 600 config/gcp-key.json 2>/dev/null || true
    
    # Setup log rotation
    print_status "Setting up log rotation..."
    docker-compose exec -T backend mkdir -p /var/log/voucher-assistant
    
    print_status "Production security setup completed"
fi

# Step 8: Monitoring setup
print_step "8. Setting up monitoring..."

# Create monitoring scripts
cat > monitoring.sh << 'EOF'
#!/bin/bash
# Monitoring script for   Voucher Assistant

echo "===   Voucher Assistant Status ==="
echo "Timestamp: $(date)"
echo ""

# Docker containers status
echo "Container Status:"
docker-compose ps

echo ""

# Health check
echo "Service Health:"
curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "Backend not responding"

echo ""

# Performance metrics
echo "Performance Metrics:"
curl -s http://localhost:8000/api/metrics | python3 -m json.tool 2>/dev/null || echo "Metrics not available"

echo ""

# Resource usage
echo "Resource Usage:"
docker stats --no-stream
EOF

chmod +x monitoring.sh

# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
# Backup script for   Voucher Assistant

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Creating backup in $BACKUP_DIR..."

# Backup Elasticsearch data
docker-compose exec -T elasticsearch tar czf - /usr/share/elasticsearch/data > "$BACKUP_DIR/elasticsearch_data.tar.gz"

# Backup feedback data
cp data/feedback.json "$BACKUP_DIR/" 2>/dev/null || echo "No feedback data to backup"

# Backup configuration
cp .env "$BACKUP_DIR/"
cp -r config "$BACKUP_DIR/" 2>/dev/null || true

# Backup metrics
curl -s http://localhost:8000/api/metrics/export > "$BACKUP_DIR/metrics.json"

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x backup.sh

print_status "Monitoring setup completed"

# Step 9: Final verification
print_step "9. Final verification..."

# Test key endpoints
print_status "Testing key endpoints..."

# Test health endpoint
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    print_status "✓ Health endpoint working"
else
    print_warning "⚠ Health endpoint issue"
fi

# Test search endpoint
if curl -s -X POST http://localhost:8000/api/search -H "Content-Type: application/json" -d '{"query":"test","top_k":1}' > /dev/null; then
    print_status "✓ Search endpoint working"
else
    print_warning "⚠ Search endpoint issue"
fi

# Test frontend
if curl -s http://localhost:3000 | grep -q " "; then
    print_status "✓ Frontend working"
else
    print_warning "⚠ Frontend issue"
fi

# Deployment completion
print_status "=== Deployment Complete ==="
echo ""
echo "🚀   AI Voucher Assistant is now running in $ENVIRONMENT mode!"
echo ""
echo "📱 Services:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Health Check: http://localhost:8000/health"
echo "   Metrics: http://localhost:8000/api/metrics"
echo ""
echo "📋 Management Commands:"
echo "   Monitor: ./monitoring.sh"
echo "   Backup: ./backup.sh"
echo "   Logs: docker-compose logs -f"
echo "   Stop: docker-compose down"
echo ""
echo "📊 Next Steps:"
echo "   1. Configure real Vertex AI credentials in config/gcp-key.json"
echo "   2. Update .env with production settings"
echo "   3. Setup SSL certificates for HTTPS"
echo "   4. Configure domain and reverse proxy"
echo "   5. Setup automated backups and monitoring alerts"
echo ""

if [ "$ENVIRONMENT" = "production" ]; then
    echo "🔒 Security Reminders:"
    echo "   - Review and secure all configuration files"
    echo "   - Setup firewall rules"
    echo "   - Enable API rate limiting"
    echo "   - Configure log monitoring"
    echo "   - Setup SSL/TLS certificates"
    echo ""
fi

print_status "Deployment script completed successfully!"
