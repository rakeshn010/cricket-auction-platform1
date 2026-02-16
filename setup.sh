#!/bin/bash

# Cricket Auction Platform - Setup Script
# This script helps set up the development environment

set -e

echo "🏏 Cricket Auction Platform - Setup Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"
else
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Check MongoDB
echo ""
echo "📋 Checking MongoDB..."
if command -v mongosh &> /dev/null || command -v mongo &> /dev/null; then
    echo -e "${GREEN}✓${NC} MongoDB client found"
else
    echo -e "${YELLOW}⚠${NC} MongoDB client not found. Make sure MongoDB is installed and running."
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${YELLOW}⚠${NC} Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓${NC} pip upgraded"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"

# Create .env file
echo ""
echo "⚙️  Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    
    # Generate random JWT secret
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Update .env with generated secret
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-super-secret-jwt-key-change-this-in-production/$JWT_SECRET/" .env
    else
        # Linux
        sed -i "s/your-super-secret-jwt-key-change-this-in-production/$JWT_SECRET/" .env
    fi
    
    echo -e "${GREEN}✓${NC} .env file created with random JWT secret"
    echo -e "${YELLOW}⚠${NC} Please review and update .env file with your settings"
else
    echo -e "${YELLOW}⚠${NC} .env file already exists"
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p uploads
echo -e "${GREEN}✓${NC} Directories created"

# Setup MongoDB indexes
echo ""
echo "🗄️  Setting up MongoDB indexes..."
read -p "Do you want to setup MongoDB indexes now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 << EOF
from pymongo import MongoClient
from core.config import settings

try:
    client = MongoClient(settings.DATABASE_URL)
    db = client[settings.DB_NAME]
    
    # Create indexes
    db.users.create_index("email", unique=True)
    db.bid_history.create_index([("player_id", 1), ("timestamp", -1)])
    db.bid_history.create_index([("team_id", 1)])
    
    print("${GREEN}✓${NC} MongoDB indexes created")
except Exception as e:
    print(f"${RED}✗${NC} Error creating indexes: {e}")
EOF
fi

# Run tests
echo ""
echo "🧪 Running tests..."
read -p "Do you want to run tests now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pytest tests/ -v
fi

# Summary
echo ""
echo "=========================================="
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Review and update .env file:"
echo "   nano .env"
echo ""
echo "2. Start MongoDB (if not running):"
echo "   sudo systemctl start mongodb"
echo ""
echo "3. Run the development server:"
echo "   source venv/bin/activate"
echo "   uvicorn main_new:app --reload"
echo ""
echo "4. Access the application:"
echo "   http://localhost:8000"
echo ""
echo "5. View API documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Project overview"
echo "   - API_DOCUMENTATION.md - API reference"
echo "   - DEPLOYMENT.md - Deployment guide"
echo "   - MIGRATION_GUIDE.md - Migration instructions"
echo ""
echo "🐳 Docker Alternative:"
echo "   docker-compose up -d"
echo ""
echo "Happy coding! 🚀"
