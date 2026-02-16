#!/bin/bash
# Quick Start Script for Cricket Auction Platform
# Run with: bash scripts/quick_start.sh

set -e  # Exit on error

echo "========================================="
echo "Cricket Auction Platform - Quick Start"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ .env file created from .env.example"
    else
        echo "⚠ Warning: .env.example not found"
        echo "Creating basic .env file..."
        cat > .env << EOF
ENVIRONMENT=development
DEBUG=true
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
MONGODB_URL=mongodb://localhost:27017/cricket_auction
ENABLE_REDIS=false
EOF
        echo "✓ Basic .env file created"
    fi
    echo ""
    echo "⚠ IMPORTANT: Edit .env file with your configuration"
fi

# Check MongoDB
echo ""
echo "Checking MongoDB connection..."
if command -v mongosh &> /dev/null; then
    if mongosh --eval "db.version()" --quiet > /dev/null 2>&1; then
        echo "✓ MongoDB is running"
    else
        echo "⚠ Warning: MongoDB is not running"
        echo "  Start MongoDB with: sudo systemctl start mongod"
    fi
else
    echo "⚠ Warning: mongosh not found"
    echo "  Install MongoDB: https://www.mongodb.com/docs/manual/installation/"
fi

# Create admin user
echo ""
read -p "Create admin user? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python create_admin.py
fi

# Run tests
echo ""
read -p "Run tests? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing test dependencies..."
    pip install pytest pytest-asyncio httpx
    echo "Running tests..."
    pytest tests/ -v
fi

echo ""
echo "========================================="
echo "Setup Complete! 🎉"
echo "========================================="
echo ""
echo "To start the server:"
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo "  2. Start server:"
echo "     python main_new.py"
echo ""
echo "Or use the start script:"
echo "  bash start_server.bat  (Windows)"
echo "  bash scripts/start_server.sh  (Linux/Mac)"
echo ""
echo "Server will be available at:"
echo "  http://localhost:8000"
echo ""
echo "Admin credentials:"
echo "  Email: admin@cricket.com"
echo "  Password: admin123"
echo ""
echo "Documentation:"
echo "  - README.md - Project overview"
echo "  - DEPLOYMENT_GUIDE.md - Production deployment"
echo "  - PRODUCTION_READY_CHECKLIST.md - Production checklist"
echo ""
