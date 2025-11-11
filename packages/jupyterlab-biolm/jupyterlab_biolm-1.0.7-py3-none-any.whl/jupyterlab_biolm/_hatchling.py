"""
Hatchling build hook to include labextension files
"""
from pathlib import Path


def get_shared_data():
    """Return shared-data mapping for labextension files"""
    root = Path(__file__).parent.parent
    shared_data = {}
    
    # Add labextension directory recursively
    labextension_dir = root / "jupyterlab_biolm" / "labextension"
    if labextension_dir.exists():
        for file_path in labextension_dir.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(labextension_dir)
                source = f"jupyterlab_biolm/labextension/{rel_path}"
                dest = f"share/jupyter/labextensions/jupyterlab-biolm/{rel_path}"
                shared_data[source] = dest
    
    # Add install.json
    install_json = root / "install.json"
    if install_json.exists():
        shared_data["install.json"] = "share/jupyter/labextensions/jupyterlab-biolm/install.json"
    
    # Add schema files
    schema_dir = root / "schema"
    if schema_dir.exists():
        for file_path in schema_dir.glob("*.json"):
            rel_path = file_path.relative_to(schema_dir)
            source = f"schema/{rel_path}"
            dest = f"share/jupyter/lab/schemas/jupyterlab-biolm/{rel_path}"
            shared_data[source] = dest
    
    return shared_data

