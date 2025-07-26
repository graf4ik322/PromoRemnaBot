#!/bin/bash

# Docker Diagnostics Script for PromoRemnaBot

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Docker Diagnostics for PromoRemnaBot${NC}"
echo "=========================================="

# Function to check system info
check_system() {
    echo -e "${BLUE}📋 System Information:${NC}"
    echo "OS: $(uname -s)"
    echo "Kernel: $(uname -r)"
    echo "Architecture: $(uname -m)"
    echo ""
}

# Function to check Docker installation
check_docker_installation() {
    echo -e "${BLUE}🐳 Docker Installation Check:${NC}"
    
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✅ Docker is installed${NC}"
        echo "Docker version: $(docker --version)"
    else
        echo -e "${RED}❌ Docker is not installed${NC}"
        return 1
    fi
    
    # Check Docker daemon
    if docker info &> /dev/null; then
        echo -e "${GREEN}✅ Docker daemon is running${NC}"
    else
        echo -e "${RED}❌ Docker daemon is not running${NC}"
        echo -e "${YELLOW}Try: sudo systemctl start docker${NC}"
        return 1
    fi
    
    # Check Docker Compose
    echo ""
    echo -e "${BLUE}🔧 Docker Compose Check:${NC}"
    
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version)
        echo -e "${GREEN}✅ docker-compose is available${NC}"
        echo "Version: $COMPOSE_VERSION"
        
        # Check if it's working
        if docker-compose --version &> /dev/null; then
            echo -e "${GREEN}✅ docker-compose is functional${NC}"
        else
            echo -e "${RED}❌ docker-compose has issues${NC}"
        fi
    fi
    
    if docker compose version &> /dev/null; then
        COMPOSE_V2_VERSION=$(docker compose version)
        echo -e "${GREEN}✅ docker compose (v2) is available${NC}"
        echo "Version: $COMPOSE_V2_VERSION"
    fi
    
    echo ""
}

# Function to check environment
check_environment() {
    echo -e "${BLUE}📄 Environment Check:${NC}"
    
    if [ -f ".env" ]; then
        echo -e "${GREEN}✅ .env file exists${NC}"
        echo "Required variables check:"
        
        # Check for required variables
        required_vars=("TELEGRAM_BOT_TOKEN" "REMNAWAVE_BASE_URL" "REMNAWAVE_TOKEN")
        for var in "${required_vars[@]}"; do
            if grep -q "^${var}=" .env; then
                echo -e "  ${GREEN}✅ ${var} is set${NC}"
            else
                echo -e "  ${RED}❌ ${var} is missing${NC}"
            fi
        done
        
        # Check DEFAULT_INBOUND_IDS format
        if grep -q "^DEFAULT_INBOUND_IDS=" .env; then
            inbound_ids=$(grep "^DEFAULT_INBOUND_IDS=" .env | cut -d'=' -f2)
            echo -e "  ${GREEN}✅ DEFAULT_INBOUND_IDS is set: $inbound_ids${NC}"
            
            # Validate format
            if [[ "$inbound_ids" =~ ^[0-9,\ ]+$ ]]; then
                echo -e "    ${GREEN}✓ Numeric format detected${NC}"
            elif [[ "$inbound_ids" =~ ^[a-f0-9\-,\ ]+$ ]]; then
                echo -e "    ${GREEN}✓ UUID format detected${NC}"
            else
                echo -e "    ${YELLOW}⚠️  Mixed or unknown format${NC}"
            fi
        else
            echo -e "  ${YELLOW}⚠️  DEFAULT_INBOUND_IDS not set (will use default)${NC}"
        fi
    else
        echo -e "${RED}❌ .env file not found${NC}"
        if [ -f ".env.example" ]; then
            echo -e "${YELLOW}💡 .env.example exists - copy it to .env${NC}"
        fi
    fi
    
    echo ""
}

# Function to check Docker Compose files
check_compose_files() {
    echo -e "${BLUE}📦 Docker Compose Files Check:${NC}"
    
    files=("docker-compose.yml" "docker-compose.prod.yml")
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}✅ $file exists${NC}"
            
            # Try to validate the file
            if command -v docker-compose &> /dev/null; then
                if docker-compose -f "$file" config &> /dev/null; then
                    echo -e "  ${GREEN}✅ $file is valid${NC}"
                else
                    echo -e "  ${RED}❌ $file has syntax errors${NC}"
                    echo -e "  ${YELLOW}Run: docker-compose -f $file config${NC}"
                fi
            elif docker compose version &> /dev/null; then
                if docker compose -f "$file" config &> /dev/null; then
                    echo -e "  ${GREEN}✅ $file is valid${NC}"
                else
                    echo -e "  ${RED}❌ $file has syntax errors${NC}"
                    echo -e "  ${YELLOW}Run: docker compose -f $file config${NC}"
                fi
            fi
        else
            echo -e "${RED}❌ $file not found${NC}"
        fi
    done
    
    echo ""
}

# Function to check network connectivity
check_connectivity() {
    echo -e "${BLUE}🌐 Network Connectivity Check:${NC}"
    
    # Check internet connectivity
    if curl -s --connect-timeout 5 https://api.telegram.org > /dev/null; then
        echo -e "${GREEN}✅ Can reach Telegram API${NC}"
    else
        echo -e "${RED}❌ Cannot reach Telegram API${NC}"
        echo -e "${YELLOW}Check your internet connection${NC}"
    fi
    
    # Check Docker Hub connectivity
    if curl -s --connect-timeout 5 https://hub.docker.com > /dev/null; then
        echo -e "${GREEN}✅ Can reach Docker Hub${NC}"
    else
        echo -e "${RED}❌ Cannot reach Docker Hub${NC}"
        echo -e "${YELLOW}May affect image pulling${NC}"
    fi
    
    echo ""
}

# Function to check for common issues
check_common_issues() {
    echo -e "${BLUE}🔧 Common Issues Check:${NC}"
    
    # Check for permission issues
    if [ -w "." ]; then
        echo -e "${GREEN}✅ Directory is writable${NC}"
    else
        echo -e "${RED}❌ Directory is not writable${NC}"
        echo -e "${YELLOW}Check permissions: chmod 755 .${NC}"
    fi
    
    # Check for Docker socket issues
    if docker ps &> /dev/null; then
        echo -e "${GREEN}✅ Can list Docker containers${NC}"
    else
        echo -e "${RED}❌ Cannot list Docker containers${NC}"
        echo -e "${YELLOW}Try: sudo usermod -aG docker \$USER && newgrp docker${NC}"
    fi
    
    # Check for port conflicts
    if netstat -ln 2>/dev/null | grep -q ":8080"; then
        echo -e "${YELLOW}⚠️  Port 8080 is in use${NC}"
        echo -e "${YELLOW}May cause conflicts if app uses this port${NC}"
    fi
    
    # Check for bot.log directory issue
    if [ -d "bot.log" ]; then
        echo -e "${RED}❌ bot.log exists as directory${NC}"
        echo -e "${YELLOW}This will cause logging errors. Remove with: rm -rf bot.log${NC}"
    elif [ -f "bot.log" ]; then
        echo -e "${YELLOW}⚠️  Old bot.log file exists${NC}"
        echo -e "${YELLOW}Logs are now in logs/bot.log directory${NC}"
    fi
    
    # Check directory permissions
    if [ -d "logs" ]; then
        if [ -w "logs" ]; then
            echo -e "${GREEN}✅ logs/ directory is writable${NC}"
        else
            echo -e "${RED}❌ logs/ directory is not writable${NC}"
            echo -e "${YELLOW}Fix with: chmod 755 logs/${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  logs/ directory missing${NC}"
    fi
    
    if [ -d "subscription_files" ]; then
        if [ -w "subscription_files" ]; then
            echo -e "${GREEN}✅ subscription_files/ directory is writable${NC}"
        else
            echo -e "${RED}❌ subscription_files/ directory is not writable${NC}"
            echo -e "${YELLOW}Fix with: chmod 755 subscription_files/${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  subscription_files/ directory missing${NC}"
    fi
    
    echo ""
}

# Function to show recommendations
show_recommendations() {
    echo -e "${BLUE}💡 Recommendations:${NC}"
    echo ""
    echo "1. If you get 'http+docker' error:"
    echo "   - Update Docker Compose: sudo apt-get update && sudo apt-get install docker-compose"
    echo "   - Or use Docker Compose v2: docker compose instead of docker-compose"
    echo ""
    echo "2. If containers fail to start:"
    echo "   - Check .env file configuration"
    echo "   - Verify network connectivity"
    echo "   - Check Docker daemon status: sudo systemctl status docker"
    echo ""
    echo "3. For permission issues:"
    echo "   - Add user to docker group: sudo usermod -aG docker \$USER"
    echo "   - Restart terminal session"
    echo ""
    echo "4. For debugging:"
    echo "   - View logs: docker logs promo-remna-bot"
    echo "   - Test configuration: docker compose config"
    echo "   - Manual build: docker build -t promo-remna-bot ."
    echo ""
}

# Main execution
main() {
    check_system
    check_docker_installation
    check_environment
    check_compose_files
    check_connectivity
    check_common_issues
    show_recommendations
    
    echo -e "${GREEN}🎉 Diagnostics completed!${NC}"
    echo -e "${YELLOW}If issues persist, share this output when asking for help.${NC}"
}

# Run main function
main