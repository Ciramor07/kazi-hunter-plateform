#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🎯 Démarrage Kazi Hunter...${NC}"

sudo systemctl start ollama
sleep 2

cd ~/kazi-hunter
docker compose up -d dashboard

echo -e "${GREEN}✅ Kazi Hunter démarré !${NC}"
echo "   Dashboard : http://localhost:8501"
