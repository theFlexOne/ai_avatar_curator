import sys
import streamlit as st
from pathlib import Path
import yaml

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from src.storage import StorageManager  # noqa: E402
from src.schemas import ProcessingStatus  # noqa: E402

def main():
    st.set_page_config(layout="wide", page_title="AI Avatar Curator")
    st.title("AI Avatar Curator 🎨")

    # --- Load Project State ---
    config_path = Path("config.yaml")
    if not config_path.exists():
        st.error("config.yaml not found in root directory.")
        return

    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)
        
    paths = config_data.get("paths", {})
    metadata_dir = Path(paths.get("metadata_file", "data/metadata.json")).parent
    
    # Scan for available subjects
    metadata_files = list(metadata_dir.glob("*_metadata.json"))
    subjects = [f.name.replace("_metadata.json", "").replace("_", " ") for f in metadata_files]
    
    if not subjects:
        st.info("No subject metadata found. Run the scraper first.")
        return

    subject_name = st.sidebar.selectbox("Select a subject to curate:", subjects)
    subject_slug = subject_name.lower().replace(" ", "_")
    
    subject_metadata_file = metadata_dir / f"{subject_slug}_metadata.json"
    storage = StorageManager(str(subject_metadata_file))
    state = storage.load_state(subject_name)

    if not state.images:
        st.info(f"No metadata found for subject '{subject_name}'.")
        return
        
    # --- Statistics ---
    total = len(state.images)
    processed = sum(1 for m in state.images.values() if m.status == ProcessingStatus.PROCESSED)
    approved = sum(1 for a in state.avatars.values() if a.is_approved)
    
    st.sidebar.metric("Total Images", total)
    st.sidebar.metric("Processed", processed)
    st.sidebar.metric("Approved", approved)

    if st.sidebar.button("Save Changes"):
        storage.save_state(state)
        st.sidebar.success("State saved!")

    # --- Image Gallery ---
    st.header(f"Curation Gallery: {subject_name}")
    
    # Filter for processed avatars
    avatars = list(state.avatars.values())

    if not avatars:
        st.warning("No images have been processed yet for this subject.")
        return

    # Create columns for the gallery
    cols = st.columns(4) 
    for i, avatar in enumerate(avatars):
        col = cols[i % 4]
        
        metadata = avatar.metadata
        image_path = Path(avatar.cropped_file_path)
        
        if image_path.exists():
            with col:
                st.image(str(image_path), width="stretch")
                
                # Show metrics
                if avatar.face_metrics:
                    m = avatar.face_metrics
                    st.caption(f"📏 Size: {m.face_size}px | ✨ Sharpness: {m.sharpness_score:.1f}")
                    if m.similarity_score is not None:
                        st.caption(f"👤 Similarity: {m.similarity_score:.2%}")

                # Approval Toggle
                is_approved = st.checkbox("Approve", value=avatar.is_approved, key=f"approve_{metadata.image_hash}")
                if is_approved != avatar.is_approved:
                    avatar.is_approved = is_approved
                    st.rerun()
        else:
            col.warning(f"Image not found: {image_path.name}")


if __name__ == "__main__":
    main()
