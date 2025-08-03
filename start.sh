#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Trading Bot Platform with Docker Compose${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Create external network if it doesn't exist
if ! docker network ls | grep -q "traefik-public"; then
    echo -e "${YELLOW}📦 Creating traefik-public network...${NC}"
    docker network create traefik-public
fi

# Create letsencrypt directory if it doesn't exist
if [ ! -d "./letsencrypt" ]; then
    echo -e "${YELLOW}📁 Creating letsencrypt directory...${NC}"
    mkdir -p letsencrypt
fi

# Create backend data directory if it doesn't exist
if [ ! -d "./backend/data" ]; then
    echo -e "${YELLOW}📁 Creating backend data directory...${NC}"
    mkdir -p backend/data
fi

# Build and start services
echo -e "${YELLOW}🔨 Building and starting services...${NC}"
docker-compose up --build -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 10

# Check service health
echo -e "${YELLOW}🔍 Checking service health...${NC}"

# Check Traefik
if curl -f http://localhost:8080 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Traefik is running on http://localhost:8080${NC}"
else
    echo -e "${RED}❌ Traefik is not responding${NC}"
fi

# Check Backend
if curl -f http://localhost/api/v1/backtest/strategies > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API is running on http://api.localhost${NC}"
else
    echo -e "${RED}❌ Backend API is not responding${NC}"
fi

# Check Frontend
if curl -f http://localhost > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is running on http://localhost${NC}"
else
    echo -e "${RED}❌ Frontend is not responding${NC}"
fi

echo -e "${GREEN}🎉 Trading Bot Platform is ready!${NC}"
echo -e "${YELLOW}📊 Access points:${NC}"
echo -e "   Frontend: http://localhost"
echo -e "   Backend API: http://api.localhost"
echo -e "   Traefik Dashboard: http://traefik.localhost:8080"
echo -e "   API Documentation: http://api.localhost/docs"
echo -e ""
echo -e "${YELLOW}🛠️  Useful commands:${NC}"
echo -e "   View logs: docker-compose logs -f"
echo -e "   Stop services: docker-compose down"
echo -e "   Restart services: docker-compose restart"
echo -e "   Rebuild services: docker-compose up --build -d" 