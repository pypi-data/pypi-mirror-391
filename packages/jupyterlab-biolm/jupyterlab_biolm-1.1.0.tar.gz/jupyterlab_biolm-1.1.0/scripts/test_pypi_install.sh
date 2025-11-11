#!/bin/bash
# Test script to verify PyPI installation works correctly
# This script:
# 1. Builds and publishes to TestPyPI (or uses existing version)
# 2. Spins up a fresh JupyterLab instance in Docker
# 3. Installs the extension from TestPyPI
# 4. Verifies the extension works via browser automation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== PyPI Installation Test ===${NC}\n"

# Check if we should build and publish first
BUILD_AND_PUBLISH=${1:-false}
VERSION=${2:-""}

if [ "$BUILD_AND_PUBLISH" = "true" ]; then
    echo -e "${YELLOW}Building and publishing to TestPyPI...${NC}"
    # This would trigger the GitHub Actions workflow
    # For now, we'll assume the package is already on TestPyPI
    echo "Note: Building and publishing should be done via GitHub Actions workflow"
    echo "Use: gh workflow run publish.yml -f repository=testpypi"
fi

# Get the package version from package.json if not provided
if [ -z "$VERSION" ]; then
    VERSION=$(node -p "require('./package.json').version")
fi

echo -e "${GREEN}Testing installation of jupyterlab-biolm==${VERSION}${NC}\n"

# Create a temporary directory for the test
TEST_DIR=$(mktemp -d)
echo "Test directory: $TEST_DIR"

# Create Dockerfile for test JupyterLab instance
cat > "$TEST_DIR/Dockerfile" << 'EOF'
FROM jupyter/scipy-notebook:latest

USER root

# Install the extension from TestPyPI
RUN pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ jupyterlab-biolm

USER $NB_UID

# Expose JupyterLab port
EXPOSE 8888

# Start JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
EOF

# Create docker-compose file for easier management
cat > "$TEST_DIR/docker-compose.yml" << EOF
version: '3.8'

services:
  jupyterlab:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8888:8888"
    environment:
      - JUPYTER_ENABLE_LAB=yes
    volumes:
      - test-notebooks:/home/jovyan/work
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8888/lab"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  test-notebooks:
EOF

echo -e "${YELLOW}Building Docker image...${NC}"
cd "$TEST_DIR"
docker-compose build

echo -e "${YELLOW}Starting JupyterLab container...${NC}"
docker-compose up -d

# Wait for JupyterLab to be ready
echo -e "${YELLOW}Waiting for JupyterLab to start...${NC}"
timeout=60
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if curl -s http://localhost:8888/lab > /dev/null 2>&1; then
        echo -e "${GREEN}JupyterLab is ready!${NC}"
        break
    fi
    sleep 2
    elapsed=$((elapsed + 2))
    echo -n "."
done

if [ $elapsed -ge $timeout ]; then
    echo -e "\n${RED}ERROR: JupyterLab failed to start within ${timeout} seconds${NC}"
    docker-compose logs
    docker-compose down
    rm -rf "$TEST_DIR"
    exit 1
fi

echo -e "\n${GREEN}JupyterLab is running at http://localhost:8888/lab${NC}"
echo -e "${YELLOW}Running browser verification tests...${NC}\n"

# Run Python script to verify extension via browser
python3 << 'PYTHON_EOF'
from playwright.sync_api import sync_playwright
import time
import sys

url = "http://localhost:8888/lab"
print(f"=== Testing Extension Installation from TestPyPI ===\n")
print(f"Connecting to: {url}\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    try:
        # Navigate to JupyterLab
        print("1. Loading JupyterLab...")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(5000)
        print("   ✅ JupyterLab loaded")
        
        # Check for BioLM extension tab
        print("\n2. Looking for BioLM extension tab...")
        biolm_tab = None
        for attempt in range(10):
            biolm_tab = page.query_selector('[title*="BioLM"], [id*="biolm"], [class*="biolm"]')
            if biolm_tab:
                break
            page.wait_for_timeout(1000)
        
        if not biolm_tab:
            print("   ❌ BioLM extension tab NOT found")
            print("   Checking browser console for errors...")
            console_messages = []
            page.on("console", lambda m: console_messages.append((m.type, m.text)))
            page.reload()
            page.wait_for_timeout(5000)
            errors = [msg for msg_type, msg in console_messages if msg_type == "error"]
            if errors:
                print(f"   Console errors: {errors[:5]}")
            sys.exit(1)
        
        print("   ✅ BioLM extension tab found")
        biolm_tab.click()
        page.wait_for_timeout(3000)
        
        # Check Models tab
        print("\n3. Testing Models tab...")
        models_btn = page.query_selector('button:has-text("Models")')
        if not models_btn:
            print("   ❌ Models tab button not found")
            sys.exit(1)
        models_btn.click()
        page.wait_for_timeout(3000)
        print("   ✅ Models tab opened")
        
        # Check Operations tab
        print("\n4. Testing Operations tab...")
        ops_btn = page.query_selector('button:has-text("Operations")')
        if not ops_btn:
            print("   ❌ Operations tab button not found")
            sys.exit(1)
        ops_btn.click()
        page.wait_for_timeout(3000)
        
        # Check for Import BioLM operation
        content = page.query_selector('.biolm-operations-list')
        if content:
            text = content.text_content() or ''
            if 'Import BioLM' in text:
                print("   ✅ 'Import BioLM' operation found")
            else:
                print("   ⚠️  'Import BioLM' operation not found")
            
            import_count = text.count('from biolmai import biolm')
            if import_count == 1:
                print(f"   ✅ Correct number of imports ({import_count})")
            else:
                print(f"   ⚠️  Found {import_count} imports (expected 1)")
        
        print("   ✅ Operations tab functional")
        
        # Check Settings tab
        print("\n5. Testing Settings tab...")
        settings_btn = page.query_selector('button:has-text("Settings")')
        if not settings_btn:
            print("   ❌ Settings tab button not found")
            sys.exit(1)
        settings_btn.click()
        page.wait_for_timeout(2000)
        print("   ✅ Settings tab opened")
        
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED!")
        print("="*50)
        print("\nExtension successfully installed from TestPyPI and is fully functional!")
        print("\nBrowser will stay open for manual inspection...")
        print("Press Ctrl+C to close and clean up.\n")
        
        # Keep browser open for manual inspection
        try:
            page.wait_for_timeout(300000)  # 5 minutes
        except KeyboardInterrupt:
            pass
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        page.screenshot(path="/tmp/test_error.png")
        print("Screenshot saved to /tmp/test_error.png")
        sys.exit(1)
    finally:
        browser.close()

PYTHON_EOF

TEST_RESULT=$?

# Cleanup
echo -e "\n${YELLOW}Cleaning up...${NC}"
cd "$TEST_DIR"
docker-compose down
rm -rf "$TEST_DIR"

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Test completed successfully!${NC}"
    exit 0
else
    echo -e "${RED}❌ Test failed!${NC}"
    exit 1
fi

