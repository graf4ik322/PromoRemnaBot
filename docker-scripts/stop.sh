#!/bin/bash

# Remnawave Telegram Bot - Docker Stop Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Stopping Remnawave Telegram Bot${NC}"
echo "=================================="

# Function to stop containers
stop_containers() {
    local compose_file="docker-compose.yml"
    local remove_volumes=false
    
    # Parse arguments
    for arg in "$@"; do
        case $arg in
            --prod)
                compose_file="docker-compose.prod.yml"
                ;;
            --remove-volumes)
                remove_volumes=true
                ;;
        esac
    done
    
    echo -e "${YELLOW}Using compose file: ${compose_file}${NC}"
    
    # Check if compose file exists
    if [ ! -f "$compose_file" ]; then
        echo -e "${RED}❌ Compose file ${compose_file} not found!${NC}"
        exit 1
    fi
    
    # Stop containers
    echo -e "${BLUE}🛑 Stopping containers...${NC}"
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$compose_file" down
    else
        docker compose -f "$compose_file" down
    fi
    
    # Remove volumes if requested
    if [ "$remove_volumes" = true ]; then
        echo -e "${YELLOW}🗑️  Removing volumes...${NC}"
        if command -v docker-compose &> /dev/null; then
            docker-compose -f "$compose_file" down -v
        else
            docker compose -f "$compose_file" down -v
        fi
    fi
    
    echo -e "${GREEN}✅ Containers stopped successfully!${NC}"
}

# Function to show help
show_help() {
    echo -e "${BLUE}Usage: $0 [OPTIONS]${NC}"
    echo ""
    echo "Options:"
    echo "  --prod             Stop production containers"
    echo "  --remove-volumes   Remove volumes as well"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                        # Stop development containers"
    echo "  $0 --prod                 # Stop production containers"
    echo "  $0 --remove-volumes       # Stop and remove volumes"
    echo "  $0 --prod --remove-volumes # Stop production and remove volumes"
}

# Function to cleanup orphaned containers
cleanup_orphans() {
    echo -e "${BLUE}🧹 Cleaning up orphaned containers...${NC}"
    
    # Remove stopped containers
    docker container prune -f
    
    # Remove unused images
    docker image prune -f
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Main execution
main() {
    case "$1" in
        --help)
            show_help
            exit 0
            ;;
    esac
    
    # Stop containers
    stop_containers "$@"
    
    # Ask if user wants to cleanup
    echo ""
    echo -e "${YELLOW}🧹 Do you want to cleanup orphaned containers and images? (y/N)${NC}"
    read -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cleanup_orphans
    fi
    
    echo ""
    echo -e "${GREEN}🎉 Bot stopped successfully!${NC}"
}

# Run main function with all arguments
main "$@"