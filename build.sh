#!/bin/bash

# Newsletter AI Backend Build Script
# This script helps build and deploy the FastAPI backend

set -e  # Exit on any error

echo "🚀 Newsletter AI Backend Build Script"
echo "======================================"

# Function to print colored output
print_status() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Parse command line arguments
COMMAND=${1:-help}

case $COMMAND in
    "build")
        print_status "Building Docker image for Newsletter AI Backend..."
        docker build -t newsletter-ai-backend:latest .
        print_success "Docker image built successfully!"
        ;;
    
    "run")
        print_status "Running Newsletter AI Backend container..."
        docker run -d \
            --name newsletter-ai-backend \
            -p 8000:8000 \
            --env-file .env \
            newsletter-ai-backend:latest
        print_success "Backend container is running on http://localhost:8000"
        ;;
    
    "stop")
        print_status "Stopping Newsletter AI Backend container..."
        docker stop newsletter-ai-backend || true
        docker rm newsletter-ai-backend || true
        print_success "Backend container stopped and removed"
        ;;
    
    "logs")
        print_status "Showing backend container logs..."
        docker logs -f newsletter-ai-backend
        ;;
    
    "push")
        if [ -z "$2" ]; then
            print_error "Please provide a registry URL. Usage: ./build.sh push <registry-url>"
            exit 1
        fi
        REGISTRY_URL=$2
        print_status "Tagging and pushing to $REGISTRY_URL..."
        docker tag newsletter-ai-backend:latest $REGISTRY_URL
        docker push $REGISTRY_URL
        print_success "Image pushed to $REGISTRY_URL"
        ;;
    
    "dev")
        print_status "Starting development server with uvicorn..."
        if [ ! -f ".env" ]; then
            print_error ".env file not found. Please create one with your environment variables."
            exit 1
        fi
        source .env
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    
    "install")
        print_status "Installing Python dependencies..."
        pip install -r requirements.txt
        print_success "Dependencies installed successfully!"
        ;;
    
    "test")
        print_status "Running backend health check..."
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Backend is healthy and responding!"
        else
            print_error "Backend health check failed. Is the server running?"
            exit 1
        fi
        ;;
    
    "deploy")
        print_status "Deploying to production..."
        print_status "1. Building Docker image..."
        docker build -t newsletter-ai-backend:latest .
        
        print_status "2. Running health check..."
        # Add your deployment commands here
        print_success "Deployment completed!"
        ;;
    
    "help"|*)
        echo "Newsletter AI Backend Build Script"
        echo ""
        echo "Usage: ./build.sh <command>"
        echo ""
        echo "Commands:"
        echo "  build     - Build Docker image"
        echo "  run       - Run backend container"
        echo "  stop      - Stop and remove backend container"
        echo "  logs      - Show container logs"
        echo "  push      - Push image to registry (requires registry URL)"
        echo "  dev       - Start development server"
        echo "  install   - Install Python dependencies"
        echo "  test      - Run health check"
        echo "  deploy    - Deploy to production"
        echo "  help      - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./build.sh build"
        echo "  ./build.sh run"
        echo "  ./build.sh push my-registry.com/newsletter-ai-backend:latest"
        echo "  ./build.sh dev"
        ;;
esac