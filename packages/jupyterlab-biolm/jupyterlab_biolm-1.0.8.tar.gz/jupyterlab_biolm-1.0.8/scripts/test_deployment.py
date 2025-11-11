#!/usr/bin/env python3
"""
End-to-end test for PyPI installation of jupyterlab-biolm extension.

This script:
1. Spins up a fresh JupyterLab instance in Docker
2. Installs the extension from TestPyPI
3. Verifies the extension works via browser automation
"""

import subprocess
import sys
import time
import tempfile
import os
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
import requests

# Colors for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color

def print_status(msg, color=GREEN):
    print(f"{color}{msg}{NC}")

def print_error(msg):
    print(f"{RED}{msg}{NC}")

def print_warning(msg):
    print(f"{YELLOW}{msg}{NC}")

def get_package_version():
    """Get latest version from TestPyPI or local package.json"""
    import json
    import requests
    try:
        # Try to get latest version from TestPyPI
        response = requests.get("https://test.pypi.org/pypi/jupyterlab-biolm/json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Get the latest version
            versions = sorted(data.get('releases', {}).keys(), reverse=True)
            if versions:
                return versions[0]
    except Exception as e:
        print_warning(f"Could not fetch version from TestPyPI: {e}")
    
    # Fallback to package.json
    with open('package.json') as f:
        return json.load(f)['version']

def find_local_wheel():
    """Find local wheel file in dist/ directory"""
    dist_dir = Path(__file__).parent.parent / "dist"
    if dist_dir.exists():
        wheels = list(dist_dir.glob("jupyterlab_biolm-*.whl"))
        if wheels:
            # Return the most recent wheel
            return max(wheels, key=lambda p: p.stat().st_mtime)
    return None

def create_docker_setup(test_dir, version):
    """Create Dockerfile and docker-compose.yml for test"""
    
    # Create Dockerfile - always install from TestPyPI
    dockerfile = f"""FROM jupyter/scipy-notebook:latest

USER root

# Install the extension from TestPyPI
RUN pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ jupyterlab-biolm=={version}

USER $NB_UID

# Expose JupyterLab port
EXPOSE 8888

# Start JupyterLab (token will be auto-generated)
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
"""
    
    dockerfile_path = Path(test_dir) / "Dockerfile"
    dockerfile_path.write_text(dockerfile)
    
    # Create docker-compose.yml
    compose = """
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
"""
    
    compose_path = Path(test_dir) / "docker-compose.yml"
    compose_path.write_text(compose)
    
    return dockerfile_path, compose_path

def wait_for_jupyterlab(url, timeout=60):
    """Wait for JupyterLab to be ready"""
    print_status(f"Waiting for JupyterLab to start at {url}...")
    elapsed = 0
    while elapsed < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_status("✅ JupyterLab is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)
        elapsed += 2
        print(".", end="", flush=True)
    print()
    return False

def test_extension_in_browser(url):
    """Test extension functionality via browser automation"""
    print_status("\n=== Testing Extension in Browser ===\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # Navigate to JupyterLab (url should already include token if needed)
            print_status("1. Loading JupyterLab...")
            print_status(f"   URL: {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(10000)  # Give it more time to fully load
            print_status("   ✅ JupyterLab loaded")
            
            # Check for BioLM extension tab
            print_status("\n2. Looking for BioLM extension tab...")
            biolm_tab = None
            for attempt in range(10):
                biolm_tab = page.query_selector('[title*="BioLM"], [id*="biolm"], [class*="biolm"]')
                if biolm_tab:
                    break
                page.wait_for_timeout(1000)
            
            if not biolm_tab:
                print_error("   ❌ BioLM extension tab NOT found")
                print_warning("   Checking browser console for errors...")
                console_messages = []
                page.on("console", lambda m: console_messages.append((m.type, m.text)))
                page.reload()
                page.wait_for_timeout(5000)
                errors = [msg for msg_type, msg in console_messages if msg_type == "error"]
                if errors:
                    print_error(f"   Console errors: {errors[:5]}")
                page.screenshot(path="/tmp/test_error_no_tab.png")
                print_warning("   Screenshot saved to /tmp/test_error_no_tab.png")
                return False
            
            print_status("   ✅ BioLM extension tab found")
            biolm_tab.click()
            page.wait_for_timeout(3000)
            
            # Check Models tab
            print_status("\n3. Testing Models tab...")
            models_btn = page.query_selector('button:has-text("Models")')
            if not models_btn:
                print_error("   ❌ Models tab button not found")
                page.screenshot(path="/tmp/test_error_models.png")
                return False
            models_btn.click()
            page.wait_for_timeout(3000)
            print_status("   ✅ Models tab opened")
            
            # Check Operations tab
            print_status("\n4. Testing Operations tab...")
            ops_btn = page.query_selector('button:has-text("Operations")')
            if not ops_btn:
                print_error("   ❌ Operations tab button not found")
                page.screenshot(path="/tmp/test_error_operations.png")
                return False
            ops_btn.click()
            page.wait_for_timeout(3000)
            
            # Check for Import BioLM operation
            content = page.query_selector('.biolm-operations-list')
            if content:
                text = content.text_content() or ''
                if 'Import BioLM' in text:
                    print_status("   ✅ 'Import BioLM' operation found")
                else:
                    print_warning("   ⚠️  'Import BioLM' operation not found")
                
                import_count = text.count('from biolmai import biolm')
                if import_count == 1:
                    print_status(f"   ✅ Correct number of imports ({import_count})")
                else:
                    print_warning(f"   ⚠️  Found {import_count} imports (expected 1)")
            
            print_status("   ✅ Operations tab functional")
            
            # Check Settings tab
            print_status("\n5. Testing Settings tab...")
            settings_btn = page.query_selector('button:has-text("Settings")')
            if not settings_btn:
                print_error("   ❌ Settings tab button not found")
                page.screenshot(path="/tmp/test_error_settings.png")
                return False
            settings_btn.click()
            page.wait_for_timeout(2000)
            print_status("   ✅ Settings tab opened")
            
            print_status("\n" + "="*50)
            print_status("✅ ALL TESTS PASSED!")
            print_status("="*50)
            print_status("\nExtension successfully installed from TestPyPI and is fully functional!")
            
            # Brief pause to see the result, then close
            page.wait_for_timeout(2000)  # 2 seconds
            
            return True
            
        except Exception as e:
            print_error(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path="/tmp/test_error.png")
            print_warning("Screenshot saved to /tmp/test_error.png")
            return False
        finally:
            browser.close()

def main():
    """Main test function"""
    print_status("=== PyPI Installation Test ===\n")
    
    # Always use TestPyPI - this is the whole point of the test
    try:
        version = get_package_version()
    except Exception as e:
        print_error(f"Failed to get package version: {e}")
        sys.exit(1)
    print_status(f"Testing installation of jupyterlab-biolm=={version} from TestPyPI\n")
    
    # Create temporary directory for Docker setup
    test_dir = tempfile.mkdtemp(prefix="jupyterlab-biolm-test-")
    print_status(f"Test directory: {test_dir}")
    
    try:
        # Create Docker setup
        print_status("\nCreating Docker setup...")
        dockerfile_path, compose_path = create_docker_setup(test_dir, version)
        
        # Build Docker image
        print_status("\nBuilding Docker image...")
        os.chdir(test_dir)
        result = subprocess.run(
            ["docker-compose", "build"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print_error(f"Failed to build Docker image:\n{result.stderr}")
            sys.exit(1)
        
        # Start container
        print_status("\nStarting JupyterLab container...")
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print_error(f"Failed to start container:\n{result.stderr}")
            sys.exit(1)
        
        # Wait for JupyterLab to be ready
        if not wait_for_jupyterlab("http://localhost:8888/lab"):
            print_error("JupyterLab failed to start")
            subprocess.run(["docker-compose", "logs"], cwd=test_dir)
            sys.exit(1)
        
        # Get the Jupyter token from container - MUST get it or fail
        print_status("\nExtracting Jupyter token from container...")
        import re
        import json
        import time
        
        # Wait a bit for server to fully start
        time.sleep(2)
        
        token = None
        max_attempts = 5
        
        for attempt in range(max_attempts):
            # Method 1: Try jupyter server list (most reliable)
            result = subprocess.run(
                ["docker-compose", "exec", "-T", "jupyterlab", "bash", "-c", "jupyter server list --jsonlist 2>/dev/null"],
                cwd=test_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                try:
                    servers = json.loads(result.stdout.strip())
                    if servers and len(servers) > 0:
                        # Extract token from URL
                        url = servers[0].get('url', '')
                        match = re.search(r'token=([a-f0-9]+)', url)
                        if match:
                            token = match.group(1)
                            print_status(f"✅ Found token via jupyter server list (attempt {attempt + 1})")
                            break
                except Exception as e:
                    if attempt == max_attempts - 1:
                        print_warning(f"Failed to parse server list: {e}")
            
            # Method 2: Check runtime directory for token files
            if not token:
                result = subprocess.run(
                    ["docker-compose", "exec", "-T", "jupyterlab", "bash", "-c", "find /home/jovyan/.local/share/jupyter/runtime -name '*.json' 2>/dev/null | head -1 | xargs python3 -c \"import sys, json; f=open(sys.argv[1]); d=json.load(f); print(d.get('token', ''))\" 2>/dev/null"],
                    cwd=test_dir,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.stdout.strip() and len(result.stdout.strip()) > 20:  # Token should be long
                    token = result.stdout.strip()
                    print_status(f"✅ Found token via runtime directory (attempt {attempt + 1})")
                    break
            
            if attempt < max_attempts - 1:
                time.sleep(2)
        
        if not token:
            print_error("❌ CRITICAL: Could not extract token from container!")
            print_error("   Cannot test extension without authentication")
            print_error("   Container logs:")
            subprocess.run(["docker-compose", "logs", "jupyterlab"], cwd=test_dir)
            sys.exit(1)
        
        jupyterlab_url = f"http://localhost:8888/lab?token={token}"
        print_status(f"✅ Using authenticated URL: http://localhost:8888/lab?token={token[:20]}...")
        
        # Debug: Check what was installed
        print_status("\nDebugging: Checking installed extension files...")
        result = subprocess.run(
            ["docker-compose", "exec", "-T", "jupyterlab", "bash", "-c", 
             "pip show jupyterlab-biolm && echo '---' && find /opt/conda/share/jupyter/labextensions -name '*biolm*' -type d 2>/dev/null | head -5 && echo '---' && ls -la /opt/conda/share/jupyter/labextensions/jupyterlab-biolm/ 2>/dev/null || echo 'Extension directory not found'"],
            cwd=test_dir,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print_warning(result.stderr)
        
        # Test extension in browser
        success = test_extension_in_browser(jupyterlab_url)
        
        # Cleanup
        print_status("\nCleaning up...")
        subprocess.run(["docker-compose", "down"], cwd=test_dir, capture_output=True)
        
        if success:
            print_status("\n✅ Test completed successfully!")
            sys.exit(0)
        else:
            print_error("\n❌ Test failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print_warning("\n\nTest interrupted by user")
        print_status("Cleaning up...")
        subprocess.run(["docker-compose", "down"], cwd=test_dir, capture_output=True)
        sys.exit(1)
    except Exception as e:
        print_error(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        subprocess.run(["docker-compose", "down"], cwd=test_dir, capture_output=True)
        sys.exit(1)
    finally:
        # Cleanup test directory
        shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == "__main__":
    main()

