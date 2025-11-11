#!/bin/bash
# Twitter News Bot - Quick Run Script

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Twitter News Bot - Quick Launcher  ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════╝${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ No .env file found${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env with your credentials before running the bot${NC}"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if credentials are set
if [ -z "$TWITTER_API_KEY" ] || [ "$TWITTER_API_KEY" = "your_api_key_here" ]; then
    echo -e "${RED}❌ Twitter API credentials not configured${NC}"
    echo "Please edit .env file with your Twitter API credentials"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo -e "${RED}❌ OpenAI API key not configured${NC}"
    echo "Please edit .env file with your OpenAI API key"
    exit 1
fi

# Show menu
echo -e "${GREEN}Select run mode:${NC}"
echo "1. Run once (text only)"
echo "2. Run once with image"
echo "3. Run once with video placeholder"
echo "4. Run on schedule (text only)"
echo "5. Run on schedule with images"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo -e "${BLUE}🤖 Running bot once (text only)...${NC}"
        npm run once
        ;;
    2)
        echo -e "${BLUE}🎨 Running bot once with image...${NC}"
        npm run once:image
        ;;
    3)
        echo -e "${BLUE}🎬 Running bot once with video placeholder...${NC}"
        npm run once:video
        ;;
    4)
        echo -e "${BLUE}⏰ Starting scheduled bot (text only)...${NC}"
        echo "Press Ctrl+C to stop"
        npm run scheduled
        ;;
    5)
        echo -e "${BLUE}⏰🎨 Starting scheduled bot with images...${NC}"
        echo "Press Ctrl+C to stop"
        npm run scheduled:image
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

