#!/bin/bash

# Remnawave Telegram Bot - Docker Start Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Remnawave Telegram Bot - Docker Setup${NC}"
echo "=================================="

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed!${NC}"
        echo -e "${YELLOW}Please install Docker first: https://docs.docker.com/get-docker/${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed!${NC}"
        echo -e "${YELLOW}Please install Docker Compose first${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker is installed${NC}"
}

# Function to check .env file
check_env_file() {
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  .env file not found!${NC}"
        if [ -f ".env.example" ]; then
            echo -e "${BLUE}📋 Copying .env.example to .env${NC}"
            cp .env.example .env
            echo -e "${YELLOW}📝 Please edit .env file with your settings before continuing${NC}"
            echo -e "${YELLOW}Press any key after editing .env file...${NC}"
            read -n 1 -s
        else
            echo -e "${RED}❌ .env.example file not found!${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ .env file found${NC}"
    fi
}

# Function to create necessary directories
create_directories() {
    echo -e "${BLUE}📁 Creating necessary directories...${NC}"
    mkdir -p subscription_files
    mkdir -p logs
    echo -e "${GREEN}✅ Directories created${NC}"
}

# Function to start containers
start_containers() {
    local compose_file="docker-compose.yml"
    local environment="development"
    
    # Check if production flag is passed
    if [[ "$1" == "--prod" ]]; then
        compose_file="docker-compose.prod.yml"
        environment="production"
    fi
    
    echo -e "${BLUE}🚀 Starting containers (${environment})...${NC}"
    echo -e "${YELLOW}Using compose file: ${compose_file}${NC}"
    
    # Check if compose file exists
    if [ ! -f "$compose_file" ]; then
        echo -e "${RED}❌ Compose file ${compose_file} not found!${NC}"
        exit 1
    fi
    
    # Build and start containers
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$compose_file" up --build -d
    else
        docker compose -f "$compose_file" up --build -d
    fi
    
    echo -e "${GREEN}✅ Containers started successfully!${NC}"
}

# Function to show container status
show_status() {
    echo -e "${BLUE}📊 Container Status:${NC}"
    
    if command -v docker-compose &> /dev/null; then
        docker-compose ps
    else
        docker compose ps
    fi
    
    echo ""
    echo -e "${BLUE}📋 Container logs (last 10 lines):${NC}"
    docker logs remnawave-telegram-bot --tail 10
}

# Function to show help
show_help() {
    echo -e "${BLUE}Usage: $0 [OPTIONS]${NC}"
    echo ""
    echo "Options:"
    echo "  --prod     Start in production mode"
    echo "  --help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                # Start in development mode"
    echo "  $0 --prod         # Start in production mode"
    echo ""
    echo "Commands after starting:"
    echo "  docker logs remnawave-telegram-bot -f    # View logs"
    echo "  docker exec -it remnawave-telegram-bot bash  # Enter container"
    echo "  docker-compose down                       # Stop containers"
}

# Main execution
main() {
    case "$1" in
        --help)
            show_help
            exit 0
            ;;
        --prod)
            echo -e "${YELLOW}🏭 Production mode selected${NC}"
            ;;
        "")
            echo -e "${YELLOW}🔧 Development mode selected${NC}"
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
    
    # Run checks and setup
    check_docker
    check_env_file
    create_directories
    
    # Start containers
    start_containers "$1"
    
    # Show status
    echo ""
    show_status
    
    echo ""
    echo -e "${GREEN}🎉 Bot is now running!${NC}"
    echo -e "${BLUE}📋 Useful commands:${NC}"
    echo "  docker logs remnawave-telegram-bot -f    # View logs"
    echo "  docker exec -it remnawave-telegram-bot bash  # Enter container"
    echo "  docker-compose down                       # Stop containers"
}

# Run main function with all arguments
main "$@"