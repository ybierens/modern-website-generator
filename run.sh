#!/bin/bash

# Website Optimizer Docker Runner
# ===============================

set -e  # Exit on any error

echo "🚀 Website Optimizer - Docker Setup"
echo "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "="

# Check if Docker daemon is running
echo "🔍 Checking Docker daemon..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker daemon not running. Please start Docker Desktop."
    exit 1
fi
echo "✅ Docker daemon is running"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.template .env
    echo "📝 Please edit .env and add your OpenAI API key, then run this script again."
    echo "   OPENAI_API_KEY=your_actual_api_key_here"
    exit 1
fi

# Check if OpenAI API key is set
if grep -q "your_openai_api_key_here" .env; then
    echo "❌ Please update .env with your actual OpenAI API key"
    exit 1
fi

echo "✅ Environment configured"

# Build and start the container
echo "🏗️  Building and starting container..."
docker-compose up --build -d

# Wait for container to be ready
echo "⏳ Waiting for container to be ready..."
sleep 3

# Check container health
echo "🔍 Checking container health..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ Container is running successfully"
else
    echo "❌ Container failed to start"
    docker-compose logs
    exit 1
fi

echo ""
echo "🎉 Setup complete! Container is running."
echo ""
echo "📋 To run the website optimizer:"
echo "   docker-compose exec website-optimizer python website_optimizer.py"
echo ""
echo "📋 To get an interactive shell:"
echo "   docker-compose exec website-optimizer bash"
echo ""
echo "📋 To stop the container:"
echo "   docker-compose down"
echo ""
echo "📋 To view logs:"
echo "   docker-compose logs -f website-optimizer"
