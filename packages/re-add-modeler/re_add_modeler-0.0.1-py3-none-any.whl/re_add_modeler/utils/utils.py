from pathlib import Path
from datetime import datetime
import os
def get_newest_timestamp_folder(base_path: str) -> Path:
    base = Path(base_path)
    datetime_folders = []

    for entry in base.iterdir():
        if entry.is_dir():
            try:
                # Try to parse the folder name as a datetime
                dt = datetime.strptime(entry.name, "%Y-%m-%d_%H-%M-%S")
                datetime_folders.append((dt, entry))
            except ValueError:
                continue  # Skip folders that aren't datetime-formatted

    if not datetime_folders:
        raise ValueError("No valid datetime-named folders found.")

    # Get the newest based on datetime
    newest = max(datetime_folders, key=lambda x: x[0])
    return os.path.abspath(newest[1])
