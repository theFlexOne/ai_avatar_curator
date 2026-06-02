import json
import os

def trim_to_verified(metadata_file, target_count=10):
    if not os.path.exists(metadata_file):
        return

    with open(metadata_file, 'r') as f:
        data = json.load(f)

    # Get all identity-verified images, sorted by timestamp
    verified_items = sorted(
        [(h, m) for h, m in data['images'].items() if m['status'] == 'id_pass'],
        key=lambda x: x[1]['timestamp']
    )
    
    keep_hashes = set([h for h, m in verified_items[:target_count]])
    
    removed_count = 0
    new_images = {}
    for h, m in data['images'].items():
        if h in keep_hashes:
            new_images[h] = m
        else:
            if m.get('local_path') and os.path.exists(m['local_path']):
                os.remove(m['local_path'])
            removed_count += 1
            
    data['images'] = new_images
    
    with open(metadata_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Trimmed to {len(new_images)} verified images. Removed {removed_count} total images.")

if __name__ == "__main__":
    trim_to_verified("data/lahel_doll_metadata.json", 10)
