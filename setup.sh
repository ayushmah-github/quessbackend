#!/bin/bash

# HRMS Backend Startup Script

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the backend directory
BACKEND_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$BACKEND_DIR"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}HRMS Lite Backend Startup${NC}"
echo -e "${BLUE}================================${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/upgrade dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install --quiet -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating .env file from .env.example...${NC}"
    cp .env.example .env
fi

echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo -e "${BLUE}To start the server, run:${NC}"
echo -e "${GREEN}python3 -m uvicorn HrmsBackend.main:app --reload --port 8000${NC}"
echo ""
echo -e "${BLUE}API Documentation:${NC}"
echo -e "${GREEN}  - Swagger UI: http://127.0.0.1:8000/docs${NC}"
echo -e "${GREEN}  - ReDoc: http://127.0.0.1:8000/redoc${NC}"
echo ""
