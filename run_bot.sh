#!/bin/bash

# Remnawave Telegram Bot Startup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Remnawave Telegram Bot...${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo -e "${YELLOW}Please copy .env.example to .env and configure it:${NC}"
    echo "cp .env.example .env"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed!${NC}"
    exit 1
fi

# Check if required packages are installed
echo -e "${YELLOW}Checking dependencies...${NC}"
python3 -c "import telegram, remnawave_api, aiofiles, dotenv" 2>/dev/null || {
    echo -e "${RED}Error: Missing dependencies!${NC}"
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
}

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the bot
echo -e "${GREEN}Starting bot...${NC}"
python3 main.py

echo -e "${GREEN}Bot stopped.${NC}"