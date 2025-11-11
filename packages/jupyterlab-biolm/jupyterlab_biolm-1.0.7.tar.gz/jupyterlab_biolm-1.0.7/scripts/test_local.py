#!/usr/bin/env python3
"""
Test the extension in a clean Dockerized JupyterLab environment
using the locally built wheel.
"""
import os
import sys
import tempfile
import shutil
import subprocess
import time
import json
import glob
from pathlib import Path
from playwright.sync_api import sync_playwright

def create_docker_setup(test_dir):
    """Create Dockerfile and docker-compose.yml for testing"""
    dockerfile = f"""FROM jupyter/scipy-notebook:latest

USER root

# Install build tools
RUN pip install --no-cache-dir build wheel

# Copy the wheel
COPY dist/*.whl /tmp/

# Install the extension
RUN pip install --no-cache-dir /tmp/jupyterlab_biolm-*.whl

# Enable server extension
RUN jupyter server extension enable jupyterlab_biolm.serverextension --sys-prefix

USER $NB_UID

# Start JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
"""

    docker_compose = f"""services:
  jupyterlab:
    build:
      context: {test_dir}
      dockerfile: Dockerfile
    ports:
      - "8888:8888"
    volumes:
      - test-notebooks:/home/jovyan/work
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8888/lab"]
      interval: 5s
      timeout: 3s
      retries: 10
    environment:
      - JUPYTER_ENABLE_LAB=yes

volumes:
  test-notebooks:
"""

    with open(os.path.join(test_dir, "Dockerfile"), "w") as f:
        f.write(dockerfile)
    
    with open(os.path.join(test_dir, "docker-compose.yml"), "w") as f:
        f.write(docker_compose)
    
    print("✅ Created Docker setup")

def build_local_wheel():
    """Build the local wheel"""
    print("Building local wheel...")
    result = subprocess.run(
        ["python3", "-m", "build", "--wheel"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"❌ Build failed: {result.stderr}")
        sys.exit(1)
    
    # Find the wheel
    dist_dir = Path("dist")
    wheels = list(dist_dir.glob("jupyterlab_biolm-*.whl"))
    if not wheels:
        print("❌ No wheel found in dist/")
        sys.exit(1)
    
    latest_wheel = max(wheels, key=lambda p: p.stat().st_mtime)
    print(f"✅ Built wheel: {latest_wheel.name}")
    return latest_wheel

def test_extension_in_browser(url):
    """Test the extension using Playwright"""
    print("\n=== Testing Extension in Browser ===")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        console_messages = []
        page.on("console", lambda msg: console_messages.append((msg.type, msg.text)))
        
        try:
            print(f"1. Loading JupyterLab...")
            print(f"   URL: {url}")
            page.goto(url, wait_until="networkidle", timeout=60000)
            time.sleep(8)
            print("   ✅ JupyterLab loaded")
            
            print("2. Looking for BioLM extension tab...")
            biolm_tab = None
            for attempt in range(15):
                biolm_tab = (page.query_selector('[title*="BioLM" i]') or 
                            page.query_selector('[id*="biolm" i]') or
                            page.query_selector('[class*="biolm" i]'))
                if biolm_tab:
                    print(f"   ✅ BioLM extension tab found (attempt {attempt + 1})")
                    break
                time.sleep(1)
            
            if not biolm_tab:
                print("   ❌ BioLM extension tab not found")
                page.screenshot(path="/tmp/biolm_no_tab.png")
                return False
            
            print("3. Clicking BioLM tab...")
            page.evaluate("(elem) => elem.click()", biolm_tab)
            time.sleep(3)
            
            print("4. Testing Models tab...")
            models_btn = page.query_selector('button:has-text("Models")')
            if models_btn:
                page.evaluate("(elem) => elem.click()", models_btn)
                time.sleep(8)
                
                # Check console for errors
                errors = [msg for msg_type, msg in console_messages if msg_type == "error"]
                biolm_msgs = [msg for msg_type, msg in console_messages if '[BioLM]' in msg]
                server_errors = [msg for msg_type, msg in console_messages if 'Can only be used' in msg]
                
                print(f"   BioLM messages: {len(biolm_msgs)}")
                for msg in biolm_msgs:
                    print(f"     {msg}")
                
                if server_errors:
                    print(f"   ❌ ServerConnection errors: {len(server_errors)}")
                    for err in server_errors:
                        print(f"     {err}")
                    return False
                else:
                    print("   ✅ No ServerConnection errors!")
                
                # Check for models
                page_text = page.evaluate("() => document.body.innerText")
                if 'esm' in page_text.lower() or 'alphafold' in page_text.lower():
                    print("   ✅ Models appear to be loaded!")
                elif 'failed' in page_text.lower() or 'error' in page_text.lower():
                    print("   ⚠️  Error text found in page")
                    error_elem = page.query_selector('[class*="error"], [class*="message"]')
                    if error_elem:
                        print(f"     Error: {error_elem.text_content()[:100]}")
                else:
                    print("   ⚠️  No clear indication of models")
                
                page.screenshot(path="/tmp/biolm_models_test.png", full_page=True)
                print("   Screenshot: /tmp/biolm_models_test.png")
            
            print("5. Testing Operations tab...")
            ops_btn = page.query_selector('button:has-text("Operations")')
            if ops_btn:
                page.evaluate("(elem) => elem.click()", ops_btn)
                time.sleep(2)
                print("   ✅ Operations tab opened")
            
            print("6. Testing Settings tab...")
            settings_btn = page.query_selector('button:has-text("Settings")')
            if settings_btn:
                page.evaluate("(elem) => elem.click()", settings_btn)
                time.sleep(2)
                print("   ✅ Settings tab opened")
            
            print("\n" + "=" * 50)
            print("✅ ALL TESTS PASSED!")
            print("=" * 50)
            return True
            
        except Exception as e:
            print(f"\n❌ Error during browser test: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path="/tmp/biolm_test_error.png")
            return False
        finally:
            browser.close()

def get_jupyter_token(container_name):
    """Extract Jupyter token from container"""
    for attempt in range(10):
        try:
            # Try runtime directory
            result = subprocess.run(
                ["docker", "exec", container_name, "find", "/home/jovyan/.local/share/jupyter/runtime", "-name", "*.json", "-type", "f"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                runtime_file = result.stdout.strip().split('\n')[0]
                result = subprocess.run(
                    ["docker", "exec", container_name, "cat", runtime_file],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    token = data.get('token', '')
                    if token:
                        print(f"✅ Found token via runtime directory (attempt {attempt + 1})")
                        return token
            
            time.sleep(2)
        except Exception as e:
            pass
    
    return None

def main():
    print("=== Local Extension Test ===")
    print("Testing extension in clean Dockerized JupyterLab\n")
    
    # Build local wheel
    wheel = build_local_wheel()
    
    # Create test directory
    test_dir = tempfile.mkdtemp(prefix="jupyterlab-biolm-test-")
    print(f"Test directory: {test_dir}")
    
    try:
        # Copy wheel to test directory
        dist_dir = os.path.join(test_dir, "dist")
        os.makedirs(dist_dir, exist_ok=True)
        shutil.copy(wheel, dist_dir)
        
        # Create Docker setup
        create_docker_setup(test_dir)
        
        # Build and start container
        print("\nBuilding Docker image...")
        result = subprocess.run(
            ["docker", "compose", "-f", os.path.join(test_dir, "docker-compose.yml"), "build"],
            cwd=test_dir,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"❌ Failed to build Docker image:\n{result.stderr}")
            sys.exit(1)
        
        print("Starting JupyterLab container...")
        result = subprocess.run(
            ["docker", "compose", "-f", os.path.join(test_dir, "docker-compose.yml"), "up", "-d"],
            cwd=test_dir,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"❌ Failed to start container:\n{result.stderr}")
            sys.exit(1)
        
        container_name = f"{os.path.basename(test_dir)}-jupyterlab-1"
        
        # Wait for JupyterLab to start
        print("Waiting for JupyterLab to start...")
        for i in range(30):
            result = subprocess.run(
                ["docker", "exec", container_name, "curl", "-f", "http://localhost:8888/lab"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                print("✅ JupyterLab is ready!")
                break
            time.sleep(2)
        else:
            print("❌ JupyterLab did not start in time")
            sys.exit(1)
        
        # Get token
        print("Extracting Jupyter token...")
        token = get_jupyter_token(container_name)
        
        if token:
            url = f"http://localhost:8888/lab?token={token}"
        else:
            url = "http://localhost:8888/lab"
        
        print(f"✅ Using URL: {url[:50]}...")
        
        # Test in browser
        success = test_extension_in_browser(url)
        
        if success:
            print("\n✅ Extension successfully tested in clean container!")
        else:
            print("\n❌ Extension test failed")
            sys.exit(1)
        
    finally:
        # Cleanup
        print("\nCleaning up...")
        subprocess.run(
            ["docker", "compose", "-f", os.path.join(test_dir, "docker-compose.yml"), "down", "-v"],
            cwd=test_dir,
            capture_output=True
        )
        shutil.rmtree(test_dir, ignore_errors=True)
        print("✅ Cleanup complete")

if __name__ == "__main__":
    main()

