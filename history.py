# history.py
# Saves and loads the history of moved files to support the Undo feature.

import json
from pathlib import Path
import shutil

# Get the exact folder where this script is located
BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "move_history.json"

def save_move_history(moves: list):
    """Save a list of moves to the JSON file."""
    if not moves:
        return
    
    history = []
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            pass 
            
    history.append({"moves": moves})
    
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

def undo_last_operation():
    """Reads the last operation from history and moves files back."""
    if not HISTORY_FILE.exists():
        return {"success": False, "message": "No history file found.", "restored": 0, "errors": []}
        
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except Exception as e:
        return {"success": False, "message": f"Could not read history: {e}", "restored": 0, "errors": []}
        
    if not history:
        return {"success": False, "message": "History is empty. (You haven't organized anything yet).", "restored": 0, "errors": []}
        
    last_op = history.pop()
    moves = last_op.get("moves", [])
    
    restored = 0
    errors = []
    
    for move in moves:
        orig_path = Path(move["original"])
        dest_path = Path(move["destination"])
        
        if not dest_path.exists():
            errors.append((str(dest_path), "File is missing from destination."))
            continue
            
        if orig_path.exists():
            errors.append((str(orig_path), "Cannot undo: original file already exists."))
            continue
            
        try:
            orig_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(dest_path), str(orig_path))
            restored += 1
        except Exception as e:
            errors.append((str(dest_path), f"Move failed: {e}"))
            
    # Save the remaining history back
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)
        
    return {
        "success": True,
        "message": "Undo complete.",
        "restored": restored,
        "errors": errors
    }