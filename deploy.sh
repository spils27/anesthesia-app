#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Deploying Anesthesia App...${NC}"

# Pull latest changes
echo -e "${BLUE}📥 Pulling latest changes...${NC}"
git pull origin main

# Stop and remove old containers
echo -e "${BLUE}🛑 Stopping old containers...${NC}"
docker-compose down

# Build fresh images
echo -e "${BLUE}🔨 Building new images...${NC}"
docker-compose build --no-cache

# Start new containers
echo -e "${BLUE}▶️  Starting containers...${NC}"
docker-compose up -d

# Show status
echo -e "${BLUE}📊 Container status:${NC}"
docker-compose ps

echo -e "${GREEN}✅ Done! App running at http://192.168.1.81:8501${NC}"