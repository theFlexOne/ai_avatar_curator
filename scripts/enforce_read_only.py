import os
import stat
import sys
from pathlib import Path

def enforce_read_only(directory: str):
    """
    Enforces read-only permissions on a directory and its contents.
    
    :param directory: The path to the directory.
    """
    try:
        path = Path(directory)
        if not path.is_dir():
            print(f"Error: Directory not found at {directory}", file=sys.stderr)
            return 1

        # Set the directory itself to read-only for the owner
        os.chmod(path, stat.S_IRUSR | stat.S_IXUSR)

        # Set all files in the directory to read-only for the owner
        for root, dirs, files in os.walk(path):
            for name in files:
                os.chmod(os.path.join(root, name), stat.S_IRUSR)
            for name in dirs:
                os.chmod(os.path.join(root, name), stat.S_IRUSR | stat.S_IXUSR)
        
        print(f"Successfully enforced read-only permissions on {directory}")
        return 0

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python enforce_read_only.py <directory_path>", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(enforce_read_only(sys.argv[1]))
