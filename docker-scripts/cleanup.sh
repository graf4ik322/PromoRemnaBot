#!/bin/bash

# Cleanup script for PromoRemnaBot - fixes bot.log directory issue

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 PromoRemnaBot Cleanup Script${NC}"
echo "================================"

# Function to stop containers
stop_containers() {
    echo -e "${BLUE}🛑 Stopping containers...${NC}"
    
    # Try both docker-compose and docker compose
    if command -v docker-compose &> /dev/null; then
        docker-compose down -v 2>/dev/null || true
    elif docker compose version &> /dev/null; then
        docker compose down -v 2>/dev/null || true
    fi
    
    # Stop specific containers if they exist
    if docker ps -q --filter "name=promo-remna-bot" | grep -q .; then
        docker stop promo-remna-bot 2>/dev/null || true
        docker rm promo-remna-bot 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ Containers stopped${NC}"
}

# Function to fix bot.log directory issue
fix_bot_log() {
    echo -e "${BLUE}📝 Fixing bot.log issues...${NC}"
    
    # Remove bot.log if it's a directory
    if [ -d "bot.log" ]; then
        echo -e "${YELLOW}🗂️  Removing bot.log directory...${NC}"
        rm -rf bot.log
        echo -e "${GREEN}✅ bot.log directory removed${NC}"
    fi
    
    # Move old bot.log file to logs directory
    if [ -f "bot.log" ]; then
        echo -e "${YELLOW}📄 Moving old bot.log to logs/...${NC}"
        mkdir -p logs
        mv bot.log logs/bot.log.old
        echo -e "${GREEN}✅ Old log moved to logs/bot.log.old${NC}"
    fi
    
    # Ensure logs directory exists
    mkdir -p logs
    echo -e "${GREEN}✅ logs directory ready${NC}"
}

# Function to clean up volumes
clean_volumes() {
    echo -e "${BLUE}🧽 Cleaning up Docker volumes...${NC}"
    
    # Remove dangling volumes
    docker volume prune -f 2>/dev/null || true
    
    echo -e "${GREEN}✅ Volumes cleaned${NC}"
}

# Function to show status
show_status() {
    echo ""
    echo -e "${BLUE}📊 Current Status:${NC}"
    
    # Check directories
    if [ -d "logs" ]; then
        echo -e "${GREEN}✅ logs/ directory exists${NC}"
    else
        echo -e "${RED}❌ logs/ directory missing${NC}"
    fi
    
    if [ -d "subscription_files" ]; then
        echo -e "${GREEN}✅ subscription_files/ directory exists${NC}"
    else
        echo -e "${YELLOW}⚠️  subscription_files/ directory missing${NC}"
    fi
    
    # Check problematic files
    if [ -d "bot.log" ]; then
        echo -e "${RED}❌ bot.log directory still exists${NC}"
    elif [ -f "bot.log" ]; then
        echo -e "${YELLOW}⚠️  bot.log file exists${NC}"
    else
        echo -e "${GREEN}✅ No bot.log conflicts${NC}"
    fi
    
    # Check containers
    if docker ps -q --filter "name=promo-remna-bot" | grep -q .; then
        echo -e "${YELLOW}⚠️  promo-remna-bot container is running${NC}"
    else
        echo -e "${GREEN}✅ No conflicting containers${NC}"
    fi
}

# Main function
main() {
    case "$1" in
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --help, -h     Show this help message"
            echo "  --dry-run      Show what would be done without making changes"
            echo ""
            echo "This script fixes common issues:"
            echo "  - Removes bot.log directory that causes logging errors"
            echo "  - Stops conflicting containers"
            echo "  - Cleans up Docker volumes"
            echo "  - Prepares directories for proper startup"
            exit 0
            ;;
        --dry-run)
            echo -e "${YELLOW}🔍 DRY RUN - Showing what would be done:${NC}"
            echo ""
            
            if [ -d "bot.log" ]; then
                echo -e "  ${YELLOW}Would remove: bot.log directory${NC}"
            fi
            
            if [ -f "bot.log" ]; then
                echo -e "  ${YELLOW}Would move: bot.log -> logs/bot.log.old${NC}"
            fi
            
            if docker ps -q --filter "name=promo-remna-bot" | grep -q .; then
                echo -e "  ${YELLOW}Would stop: promo-remna-bot container${NC}"
            fi
            
            echo -e "  ${YELLOW}Would create: logs/ directory${NC}"
            echo -e "  ${YELLOW}Would create: subscription_files/ directory${NC}"
            echo -e "  ${YELLOW}Would clean: Docker volumes${NC}"
            
            echo ""
            echo -e "${GREEN}Run without --dry-run to apply changes${NC}"
            exit 0
            ;;
    esac
    
    echo -e "${YELLOW}⚠️  This will stop containers and clean up files${NC}"
    echo -e "${YELLOW}Are you sure you want to continue? (y/N)${NC}"
    read -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Operation cancelled${NC}"
        exit 0
    fi
    
    # Perform cleanup
    stop_containers
    fix_bot_log
    clean_volumes
    
    # Create necessary directories
    mkdir -p subscription_files
    mkdir -p logs
    
    show_status
    
    echo ""
    echo -e "${GREEN}🎉 Cleanup completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}💡 Next steps:${NC}"
    echo "  1. Start the bot: ./docker-scripts/start-safe.sh --prod"
    echo "  2. Check logs: tail -f logs/bot.log"
    echo "  3. Monitor: docker logs promo-remna-bot -f"
}

# Run main function with all arguments
main "$@"