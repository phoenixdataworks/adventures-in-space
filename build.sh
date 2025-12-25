#!/bin/bash

# Master build script for Arcade Games Collection
# This script builds all Pygame games with Pygbag and the Next.js web app

set -e

echo "🎮 Arcade Games Collection - Build Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    exit 1
fi

# Check for Node
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is required but not installed.${NC}"
    exit 1
fi

# Check for pygbag
if ! python3 -m pip show pygbag &> /dev/null; then
    echo -e "${YELLOW}⚠️  pygbag not found. Installing...${NC}"
    python3 -m pip install pygbag pygame
fi

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"
echo ""

# Build Pygame games
echo "🐍 Building Pygame games with Pygbag..."
echo "----------------------------------------"

declare -a games=(
    "adventures-in-space:main.py"
    "santa-vs-grunch:main.py"
    "snake-jump:snake-jump.py"
    "bible_stories:main.py"
    "joseph_mary_run:main.py"
)

for game_entry in "${games[@]}"; do
    IFS=':' read -r game_dir main_file <<< "$game_entry"
    
    if [ -d "$game_dir" ]; then
        echo -e "  📦 Building ${YELLOW}$game_dir${NC}..."
        cd "$game_dir"
        
        if python3 -m pygbag --build "$main_file" 2>/dev/null; then
            echo -e "     ${GREEN}✅ Success${NC}"
        else
            echo -e "     ${RED}❌ Failed${NC}"
        fi
        
        cd "$SCRIPT_DIR"
    else
        echo -e "  ⚠️  Directory not found: $game_dir"
    fi
done

echo ""

# Build Next.js web app
echo "⚛️  Building Next.js web app..."
echo "--------------------------------"

cd web-app

# Install dependencies
echo "  📥 Installing dependencies..."
npm install --silent

# Create games directory and copy built games
echo "  📁 Copying games to public folder..."
mkdir -p public/games

for game_entry in "${games[@]}"; do
    IFS=':' read -r game_dir main_file <<< "$game_entry"
    
    build_path="../$game_dir/build/web"
    if [ -d "$build_path" ]; then
        cp -r "$build_path" "public/games/$game_dir"
        echo "     ✅ Copied $game_dir"
    else
        echo "     ⚠️  Build not found: $game_dir"
    fi
done

# Build Next.js
echo "  🔨 Building Next.js..."
npm run build

cd "$SCRIPT_DIR"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Build complete!${NC}"
echo ""
echo "📁 Output locations:"
echo "   • Pygame games: <game>/build/web/"
echo "   • Next.js app:  web-app/out/"
echo ""
echo "🚀 To preview locally:"
echo "   cd web-app && npx serve out"
echo ""
echo "📤 To deploy to GitHub Pages:"
echo "   Push to main branch - GitHub Actions will handle the rest!"

