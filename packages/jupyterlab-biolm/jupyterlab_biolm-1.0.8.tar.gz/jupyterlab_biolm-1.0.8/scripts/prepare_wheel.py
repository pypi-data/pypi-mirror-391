#!/usr/bin/env python3
"""
Pre-build script to ensure labextension files are ready for packaging
"""
import sys
from pathlib import Path

def main():
    root = Path(__file__).parent.parent
    labextension_dir = root / "jupyterlab_biolm" / "labextension"
    
    if not labextension_dir.exists():
        print("ERROR: labextension directory not found. Run 'npm run build:labextension:dev' first.")
        sys.exit(1)
    
    static_dir = labextension_dir / "static"
    if not static_dir.exists() or not any(static_dir.glob("*.js")):
        print("ERROR: labextension static files not found. Run 'npm run build:labextension:dev' first.")
        sys.exit(1)
    
    print("✅ Labextension files ready for packaging")
    return 0

if __name__ == "__main__":
    sys.exit(main())

