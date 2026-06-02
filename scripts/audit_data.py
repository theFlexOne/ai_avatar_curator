import json
from pathlib import Path

def audit():
    metadata_path = Path("data/lahel_doll_metadata.json")
    if not metadata_path.exists():
        print(f"Metadata file {metadata_path} not found.")
        return

    with open(metadata_path, 'r') as f:
        data = json.load(f)

    images = data.get("images", {})
    total = len(images)
    
    stats = {}
    for img in images.values():
        status = img.get("status", "unknown")
        stats[status] = stats.get(status, 0) + 1

    print(f"Total images: {total}")
    print("Status counts:")
    for status, count in stats.items():
        print(f"  - {status}: {count}")

    print("\nFirst 5 id_pass images:")
    passes = [img for img in images.values() if img.get("status") == "id_pass"]
    for img in passes[:5]:
        print(f"  - {img.get('title')} | Source: {img.get('source_url')}")

    print("\nFailure Analysis (filtered_fail / face_fail):")
    fails = [img for img in images.values() if img.get("status") in ["filtered_fail", "face_fail"]]
    # Just show first 3 reasons if available
    for img in fails[:3]:
        print(f"  - Hash: {img.get('image_hash')} | Status: {img.get('status')} | Error: {img.get('error_message')}")

    # Check processed/interim
    interim_count = len(list(Path("data/interim").glob("*")))
    processed_count = len(list(Path("data/processed").glob("*")))
    print("\nProcessed Check:")
    print(f"  - Interim images: {interim_count}")
    print(f"  - Processed images: {processed_count}")

if __name__ == "__main__":
    audit()
