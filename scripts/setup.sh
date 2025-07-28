#!/bin/bash

# Discord Username Monitor - Setup Script for Linux/macOS
# This script sets up the environment and dependencies

set -e

echo "==================================================="
echo "Discord Username Monitor v2.0 - Setup Script"
echo "==================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.8+ first.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} detected${NC}"

# Check if version is 3.8+
if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
    echo -e "${RED}Python 3.8 or higher is required. Current version: ${PYTHON_VERSION}${NC}"
    exit 1
fi

# Check Chrome installation
echo -e "${BLUE}Checking Google Chrome installation...${NC}"
if command -v google-chrome &> /dev/null || command -v google-chrome-stable &> /dev/null || command -v chromium-browser &> /dev/null; then
    echo -e "${GREEN}✓ Chrome/Chromium detected${NC}"
else
    echo -e "${YELLOW}⚠ Chrome not detected. Installing Chrome is recommended.${NC}"
    echo -e "${YELLOW}  You can install it manually or continue without it.${NC}"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create virtual environment
echo -e "${BLUE}Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "${BLUE}Installing Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}requirements.txt not found${NC}"
    exit 1
fi

# Create directory structure
echo -e "${BLUE}Setting up directory structure...${NC}"
mkdir -p logs results data config accounts usernames proxies
echo -e "${GREEN}✓ Directories created${NC}"

# Create example files
echo -e "${BLUE}Creating example configuration files...${NC}"

# Create example tokens file
if [ ! -f "accounts/tokens.txt" ]; then
    cat > accounts/tokens.txt.example << 'EOF'
# Discord Username Monitor - Account Tokens
# 
# Supported formats:
# 1. email:password:token
# 2. email:token  
# 3. token (token only)
#
# Example entries:
# user@example.com:mypassword:MTAxNTExNjQyNzc4MzUyNjQxMA...
# user@example.com:MTAxNTExNjQyNzc4MzUyNjQxMA...
# MTAxNTExNjQyNzc4MzUyNjQxMA...

# Add your tokens below:

EOF
    echo -e "${GREEN}✓ Example tokens file created${NC}"
fi

# Create example username list
if [ ! -f "usernames/example_list.txt" ]; then
    cat > usernames/example_list.txt << 'EOF'
cool
epic
user
name
fire
star
moon
test
demo
example
EOF
    echo -e "${GREEN}✓ Example username list created${NC}"
fi

# Create gitkeep files
touch logs/.gitkeep results/.gitkeep data/.gitkeep

echo ""
echo -e "${GREEN}==================================================="
echo -e "✓ Setup completed successfully!"
echo -e "===================================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "1. Add your Discord tokens to ${YELLOW}accounts/tokens.txt${NC}"
echo -e "2. Run the monitor: ${YELLOW}python src/main.py${NC}"
echo -e "3. Follow the interactive configuration"
echo ""
echo -e "${BLUE}For help:${NC}"
echo -e "- Check the README.md file"
echo -e "- Visit the documentation in docs/"
echo -e "- Report issues on GitHub"
echo ""
echo -e "${GREEN}Happy monitoring!${NC}"


