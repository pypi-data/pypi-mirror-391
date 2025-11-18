#!/bin/bash
# CCPM Plugin Packaging Script
# Creates a distributable zip file of the CCPM plugin

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   CCPM Plugin Packaging Script            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Get version from plugin.json
VERSION=$(python3 -c "import json; print(json.load(open('ccpm/.claude-plugin/plugin.json'))['version'])")
ZIP_NAME="ccpm-v${VERSION}.zip"

echo -e "${YELLOW}📦 Packaging CCPM Plugin v${VERSION}${NC}"
echo ""

# Step 1: Regenerate catalog
echo -e "${BLUE}Step 1: Regenerating rules catalog...${NC}"
cd ccpm
python scripts/catalog-rules.py --pretty
cd ..
echo -e "${GREEN}  ✅ Catalog regenerated${NC}"
echo ""

# Step 2: Verify structure
echo -e "${BLUE}Step 2: Verifying plugin structure...${NC}"
required_dirs=(".claude-plugin" "agents" "commands" "hooks" "rules" "scripts" "learned")
all_present=true

for dir in "${required_dirs[@]}"; do
    if [ -d "ccpm/$dir" ]; then
        echo -e "${GREEN}  ✅ ccpm/$dir${NC}"
    else
        echo -e "${RED}  ❌ ccpm/$dir NOT FOUND${NC}"
        all_present=false
    fi
done

if [ "$all_present" = false ]; then
    echo -e "${RED}ERROR: Missing required directories!${NC}"
    exit 1
fi
echo ""

# Step 3: Check plugin.json
echo -e "${BLUE}Step 3: Validating plugin.json...${NC}"
if python3 -c "import json; json.load(open('ccpm/.claude-plugin/plugin.json'))" 2>/dev/null; then
    echo -e "${GREEN}  ✅ plugin.json is valid JSON${NC}"
else
    echo -e "${RED}  ❌ plugin.json is INVALID${NC}"
    exit 1
fi
echo ""

# Step 4: Create zip
echo -e "${BLUE}Step 4: Creating zip file...${NC}"
cd ccpm
zip -r ../$ZIP_NAME . -x "*.DS_Store" -x "*__pycache__*" -x "*.pyc"
cd ..
echo -e "${GREEN}  ✅ Created: $ZIP_NAME${NC}"
echo ""

# Step 5: Verify zip
echo -e "${BLUE}Step 5: Verifying zip contents...${NC}"
echo ""
echo "Top-level contents:"
unzip -l $ZIP_NAME | head -20
echo ""

# Get zip size
ZIP_SIZE=$(ls -lh $ZIP_NAME | awk '{print $5}')
echo -e "${GREEN}✅ Plugin packaged successfully!${NC}"
echo ""
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}  Package: ${GREEN}$ZIP_NAME${NC}"
echo -e "${YELLOW}  Size:    ${GREEN}$ZIP_SIZE${NC}"
echo -e "${YELLOW}  Version: ${GREEN}$VERSION${NC}"
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Installation instructions:${NC}"
echo ""
echo "  1. In Claude Code: /plugin install path/to/$ZIP_NAME"
echo "  2. Or manually:    unzip $ZIP_NAME -d .claude/plugins/ccpm/"
echo ""
echo -e "${BLUE}Testing:${NC}"
echo ""
echo "  /plugin list     # Verify ccpm is listed"
echo "  /pm:help         # Test a command"
echo ""
echo -e "${GREEN}Done!${NC}"
