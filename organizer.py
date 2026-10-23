# organizer.py
# Filesystem scanning and moving logic.

import os
import shutil
from pathlib import Path
from categories import get_category, FALLBACK_CATEGORY, all_category_names

# Import the history saver
from history import save_move_history

class ScanResult:
    def __init__(self):
        self.files = []                 # list of (Path, category)
        self.counts = {name: 0 for name in all_category_names()}
        self.errors = []                # list of (Path, error_message)

def scan_folder(source_dir: str, include_subfolders: bool,
                exclude_dir: str = None) -> ScanResult:
    """Scan source_dir for files and tag each with its category."""
    result = ScanResult()
    source = Path(source_dir).resolve()

    if not source.exists() or not source.is_dir():
        result.errors.append((source, "Folder does not exist or is not a folder"))
        return result

    excluded = Path(exclude_dir).resolve() if exclude_dir else None

    def handle_file(path: Path):
        try:
            category = get_category(path.name)
            result.files.append((path, category))
            result.counts[category] += 1
        except Exception as e:
            result.errors.append((path, str(e)))

    if include_subfolders:
        for root, dirs, files in os.walk(source, followlinks=False):
            root_path = Path(root)
            if excluded and excluded.is_relative_to(root_path):
                if excluded.name in dirs:
                    dirs.remove(excluded.name)
            for name in files:
                handle_file(root_path / name)
    else:
        try:
            for entry in source.iterdir():
                if entry.is_file():
                    handle_file(entry)
        except PermissionError as e:
            result.errors.append((source, f"Permission denied: {e}"))

    return result

def get_safe_destination(dest_folder: Path, filename: str) -> Path:
    """Generate a safe path, e.g., report_1.pdf if report.pdf exists."""
    target = dest_folder / filename
    if not target.exists():
        return target
    
    stem = target.stem
    suffix = target.suffix
    counter = 1
    while True:
        new_target = dest_folder / f"{stem}_{counter}{suffix}"
        if not new_target.exists():
            return new_target
        counter += 1

def organize_files(scan_result: ScanResult, dest_dir: str, progress_callback=None):
    """
    Moves the files found in scan_result to dest_dir/category/.
    Returns a summary dictionary and saves to history.
    """
    dest_root = Path(dest_dir).resolve()
    moved_count = 0
    errors = []
    successful_moves = [] 
    
    total = len(scan_result.files)

    for index, (file_path, category) in enumerate(scan_result.files):
        try:
            # Create category folder if it doesn't exist
            target_folder = dest_root / category
            target_folder.mkdir(parents=True, exist_ok=True)
            
            # Get safe destination path (handles duplicates)
            dest_path = get_safe_destination(target_folder, file_path.name)
            
            # Move the file
            shutil.move(str(file_path), str(dest_path))
            moved_count += 1
            
            # Record this successful move
            successful_moves.append({
                "original": str(file_path),
                "destination": str(dest_path)
            })
            
        except Exception as e:
            errors.append((file_path, str(e)))
            
        # Update progress bar
        if progress_callback:
            progress_callback(index + 1, total)

    # Save successful moves to history so we can undo them later
    if successful_moves:
        save_move_history(successful_moves)

    return {
        "moved": moved_count,
        "errors": errors,
        "total": total
    }