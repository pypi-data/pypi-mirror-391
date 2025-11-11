#!/usr/bin/env python3
"""
Start a test JupyterLab server in Docker and open it in the browser
"""
import os
import sys
import tempfile
import shutil
import subprocess
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

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
    
    dist_dir = Path("dist")
    wheels = list(dist_dir.glob("jupyterlab_biolm-*.whl"))
    if not wheels:
        print("❌ No wheel found in dist/")
        sys.exit(1)
    
    latest_wheel = max(wheels, key=lambda p: p.stat().st_mtime)
    print(f"✅ Built wheel: {latest_wheel.name}")
    return latest_wheel

def create_docker_setup(test_dir):
    """Create Dockerfile and docker-compose.yml"""
    dockerfile = f"""FROM jupyter/scipy-notebook:latest

USER root

RUN pip install --no-cache-dir build wheel

COPY dist/*.whl /tmp/

# Install the extension (server extension should auto-enable via entry points)
RUN pip install --no-cache-dir /tmp/jupyterlab_biolm-*.whl

USER $NB_UID

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--ServerApp.token=''", "--ServerApp.password=''", "--IdentityProvider.token=''"]
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

volumes:
  test-notebooks:
"""

    with open(os.path.join(test_dir, "Dockerfile"), "w") as f:
        f.write(dockerfile)
    
    with open(os.path.join(test_dir, "docker-compose.yml"), "w") as f:
        f.write(docker_compose)

def main():
    print("=== Starting Test JupyterLab Server ===\n")
    
    wheel = build_local_wheel()
    test_dir = tempfile.mkdtemp(prefix="jupyterlab-biolm-test-")
    
    try:
        dist_dir = os.path.join(test_dir, "dist")
        os.makedirs(dist_dir, exist_ok=True)
        shutil.copy(wheel, dist_dir)
        
        create_docker_setup(test_dir)
        
        print("Building Docker image...")
        result = subprocess.run(
            ["docker", "compose", "-f", os.path.join(test_dir, "docker-compose.yml"), "build"],
            cwd=test_dir,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"❌ Build failed:\n{result.stderr}")
            sys.exit(1)
        
        print("Starting container...")
        result = subprocess.run(
            ["docker", "compose", "-f", os.path.join(test_dir, "docker-compose.yml"), "up", "-d"],
            cwd=test_dir,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"❌ Failed to start:\n{result.stderr}")
            sys.exit(1)
        
        container_name = f"{os.path.basename(test_dir)}-jupyterlab-1"
        
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
            print("❌ JupyterLab did not start")
            sys.exit(1)
        
        url = "http://localhost:8888/lab"
        print(f"\n🌐 Server running at: {url}")
        print("Opening in browser...\n")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            console_messages = []
            page.on("console", lambda msg: console_messages.append((msg.type, msg.text)))
            
            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                time.sleep(8)
                
                biolm_tab = page.query_selector('[title*="BioLM" i], [id*="biolm" i]')
                if biolm_tab:
                    page.evaluate("(elem) => elem.click()", biolm_tab)
                    time.sleep(5)
                    
                    models_btn = page.query_selector('button:has-text("Models")')
                    if models_btn:
                        page.evaluate("(elem) => elem.click()", models_btn)
                        time.sleep(8)
                        
                        biolm_msgs = [msg for msg_type, msg in console_messages if '[BioLM]' in msg]
                        errors = [msg for msg_type, msg in console_messages if msg_type == "error"]
                        
                        print("=== BioLM Console Messages ===")
                        for msg in biolm_msgs:
                            print(f"  {msg}")
                        
                        if errors:
                            print("\n=== Errors ===")
                            for err in errors[:5]:
                                print(f"  {err}")
                        
                        page.screenshot(path="/tmp/biolm_server_test.png", full_page=True)
                        print(f"\n✅ Browser opened - screenshot: /tmp/biolm_server_test.png")
                
                print("\n✅ Server is running. Browser window is open.")
                print("Press Ctrl+C to stop...")
                
                # Keep running
                while True:
                    time.sleep(60)
                    
            except KeyboardInterrupt:
                print("\nStopping...")
            finally:
                browser.close()
        
    except KeyboardInterrupt:
        print("\nCleaning up...")
    finally:
        subprocess.run(
            ["docker", "compose", "-f", os.path.join(test_dir, "docker-compose.yml"), "down", "-v"],
            cwd=test_dir,
            capture_output=True
        )
        shutil.rmtree(test_dir, ignore_errors=True)
        print("✅ Cleanup complete")

if __name__ == "__main__":
    main()

