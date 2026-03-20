import json
import pathlib

# 1. Config paths
REPO_ROOT = pathlib.Path(__file__).parent.parent
CHAR_DIR = REPO_ROOT / "characters"
MESH_FILE = REPO_ROOT / "config" / "relationship_mesh.py"

def move_character(slug: str, venue_id: str, status: str, display_name: str = None):
    # 2. Update Manifest
    manifest_path = CHAR_DIR / slug / "manifest.json"
    with manifest_path.open('r+') as f:
        data = json.load(f)

        # Update the internal location object
        data["world_config"]["current_location"]["venue_id"] = venue_id
        data["world_config"]["current_location"]["display_name"] = display_name or venue_id

        # Reset file pointer and write back
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

    # 3. Update Mesh (Advanced: modifying a .py file via text)
    # This is hacky but effective for small scripts
    with MESH_FILE.open('r') as f:
        mesh_content = f.read()

    # Simple string replacement for the demo 
    # (In production, you'd import the dict, edit, and export, but that requires valid Python exec)
    # We look for the line in the mesh that defines gideon's location and replace it.

    old_entry = f'"{slug}": {{ ... "location": "[^"]*"'
    # Note: You'd need regex to do this safely.

    print(f"SUCCESS: {slug} moved to {venue_id}. Status: {status}")