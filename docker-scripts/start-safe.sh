#!/bin/bash

# Safe Docker Start Script for PromoRemnaBot
# Handles Docker Compose version conflicts and compatibility issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 PromoRemnaBot - Safe Docker Start${NC}"
echo "===================================="

# Function to detect and set the best Docker Compose command
detect_compose_command() {
    echo -e "${BLUE}🔍 Detecting Docker Compose...${NC}"
    
    # Try Docker Compose v2 first (recommended)
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
        COMPOSE_VERSION=$(docker compose version --short 2>/dev/null || echo "v2.x")
        echo -e "${GREEN}✅ Using Docker Compose v2: $COMPOSE_VERSION${NC}"
        return 0
    fi
    
    # Fall back to Docker Compose v1
    if command -v docker-compose &> /dev/null; then
        # Check if it's actually working
        if docker-compose --version &> /dev/null; then
            COMPOSE_CMD="docker-compose"
            COMPOSE_VERSION=$(docker-compose --version | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -1)
            echo -e "${YELLOW}⚠️  Using Docker Compose v1: $COMPOSE_VERSION${NC}"
            echo -e "${YELLOW}Consider upgrading to Docker Compose v2${NC}"
            return 0
        else
            echo -e "${RED}❌ docker-compose found but not working${NC}"
        fi
    fi
    
    echo -e "${RED}❌ No working Docker Compose found!${NC}"
    echo -e "${YELLOW}Please install Docker Compose:${NC}"
    echo "  - For Ubuntu/Debian: sudo apt-get install docker-compose-plugin"
    echo "  - Or follow: https://docs.docker.com/compose/install/"
    exit 1
}

# Function to validate Docker setup
validate_docker() {
    echo -e "${BLUE}🔧 Validating Docker setup...${NC}"
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        echo -e "${YELLOW}Install Docker: https://docs.docker.com/get-docker/${NC}"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker daemon is not running${NC}"
        echo -e "${YELLOW}Start Docker daemon:${NC}"
        echo "  sudo systemctl start docker"
        echo "  # or"
        echo "  sudo service docker start"
        exit 1
    fi
    
    # Check Docker permissions
    if ! docker ps &> /dev/null; then
        echo -e "${RED}❌ Cannot access Docker (permission denied)${NC}"
        echo -e "${YELLOW}Add user to docker group:${NC}"
        echo "  sudo usermod -aG docker \$USER"
        echo "  newgrp docker"
        echo "  # or restart your terminal"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker is properly configured${NC}"
}

# Function to check environment file
check_environment() {
    echo -e "${BLUE}📄 Checking environment...${NC}"
    
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  .env file not found${NC}"
        if [ -f ".env.example" ]; then
            echo -e "${BLUE}📋 Creating .env from .env.example${NC}"
            cp .env.example .env
            echo -e "${YELLOW}📝 Please edit .env file with your settings${NC}"
            echo -e "${YELLOW}Press Enter after editing .env file...${NC}"
            read -r
        else
            echo -e "${RED}❌ .env.example not found${NC}"
            exit 1
        fi
    fi
    
    # Validate required environment variables
    required_vars=("TELEGRAM_BOT_TOKEN" "REMNAWAVE_BASE_URL" "REMNAWAVE_TOKEN")
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env || grep -q "^${var}=$" .env || grep -q "^${var}=your_" .env; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        echo -e "${RED}❌ Missing or invalid environment variables:${NC}"
        printf '  - %s\n' "${missing_vars[@]}"
        echo -e "${YELLOW}Please configure these variables in .env file${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Environment is properly configured${NC}"
}

# Function to validate compose files
validate_compose_files() {
    local compose_file="$1"
    
    echo -e "${BLUE}📦 Validating $compose_file...${NC}"
    
    if [ ! -f "$compose_file" ]; then
        echo -e "${RED}❌ $compose_file not found${NC}"
        exit 1
    fi
    
    # Test compose file syntax
    if ! $COMPOSE_CMD -f "$compose_file" config &> /dev/null; then
        echo -e "${RED}❌ $compose_file has syntax errors${NC}"
        echo -e "${YELLOW}Run for details: $COMPOSE_CMD -f $compose_file config${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ $compose_file is valid${NC}"
}

# Function to create directories
create_directories() {
    echo -e "${BLUE}📁 Creating directories...${NC}"
    
    directories=("subscription_files" "logs")
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            echo -e "  ${GREEN}✅ Created $dir${NC}"
        else
            echo -e "  ${GREEN}✅ $dir exists${NC}"
        fi
        
        # Set proper permissions for Docker
        chmod 755 "$dir" 2>/dev/null || true
        echo -e "  ${GREEN}✅ Set permissions for $dir${NC}"
    done
}

# Function to pull images safely
pull_images() {
    local compose_file="$1"
    
    echo -e "${BLUE}📥 Pulling images...${NC}"
    
    # Try to pull images, but don't fail if it doesn't work
    if ! $COMPOSE_CMD -f "$compose_file" pull 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Could not pull pre-built images, will build locally${NC}"
    else
        echo -e "${GREEN}✅ Images pulled successfully${NC}"
    fi
}

# Function to start containers
start_containers() {
    local compose_file="$1"
    local environment="$2"
    
    echo -e "${BLUE}🚀 Starting containers ($environment)...${NC}"
    echo -e "${YELLOW}Using: $COMPOSE_CMD -f $compose_file${NC}"
    
    # Build and start containers
    if $COMPOSE_CMD -f "$compose_file" up --build -d; then
        echo -e "${GREEN}✅ Containers started successfully${NC}"
    else
        echo -e "${RED}❌ Failed to start containers${NC}"
        echo -e "${YELLOW}Checking logs for errors...${NC}"
        $COMPOSE_CMD -f "$compose_file" logs
        exit 1
    fi
}

# Function to show status
show_status() {
    local compose_file="$1"
    
    echo -e "${BLUE}📊 Container Status:${NC}"
    $COMPOSE_CMD -f "$compose_file" ps
    
    echo ""
    echo -e "${BLUE}📋 Recent logs:${NC}"
    $COMPOSE_CMD -f "$compose_file" logs --tail=10
}

# Function to show helpful commands
show_help() {
    echo ""
    echo -e "${BLUE}💡 Useful commands:${NC}"
    echo "  View logs:        $COMPOSE_CMD logs -f"
    echo "  Stop containers:  $COMPOSE_CMD down"
    echo "  Restart:          $COMPOSE_CMD restart"
    echo "  Enter container:  docker exec -it promo-remna-bot bash"
    echo "  Check status:     docker ps"
    echo ""
    echo -e "${GREEN}🎉 Bot is running!${NC}"
    echo -e "${YELLOW}Check logs to ensure everything is working correctly.${NC}"
}

# Main function
main() {
    local environment="development"
    local compose_file="docker-compose.yml"
    
    # Parse arguments
    case "$1" in
        --prod|--production)
            environment="production"
            compose_file="docker-compose.prod.yml"
            echo -e "${YELLOW}🏭 Production mode selected${NC}"
            ;;
        --help|-h)
            echo "Usage: $0 [--prod|--production]"
            echo "  --prod, --production  Use production configuration"
            exit 0
            ;;
        "")
            echo -e "${YELLOW}🔧 Development mode selected${NC}"
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
    
    # Run all checks and start containers
    validate_docker
    detect_compose_command
    check_environment
    validate_compose_files "$compose_file"
    create_directories
    pull_images "$compose_file"
    start_containers "$compose_file" "$environment"
    show_status "$compose_file"
    show_help
}

# Trap to handle errors
trap 'echo -e "\n${RED}❌ Script failed. Run ./docker-scripts/diagnose.sh for detailed diagnostics.${NC}"' ERR

# Run main function with all arguments
main "$@"