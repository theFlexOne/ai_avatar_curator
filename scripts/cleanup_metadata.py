import json
import os

def cleanup_metadata(metadata_file):
    if not os.path.exists(metadata_file):
        print(f"Metadata file {metadata_file} not found.")
        return

    with open(metadata_file, 'r') as f:
        data = json.load(f)

    original_count = len(data['images'])
    
    # Filter out images whose local_path does not exist
    cleaned_images = {}
    removed_count = 0
    for h, m in data['images'].items():
        local_path = m.get('local_path')
        if local_path and os.path.exists(local_path):
            cleaned_images[h] = m
        else:
            removed_count += 1
            print(f"Removing missing image from metadata: {h} ({local_path})")

    data['images'] = cleaned_images
    
    with open(metadata_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Cleanup complete. Removed {removed_count} entries. {len(cleaned_images)} entries remaining.")

if __name__ == "__main__":
    cleanup_metadata("data/lahel_doll_metadata.json")
