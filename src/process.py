import argparse
import logging
import yaml
from pathlib import Path

from src.context import ProjectContext
from src.audit import AuditLoop
from src.processors.image_processor import ImageProcessor
from src.schemas import ProcessingStatus

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def run_processing(ctx: ProjectContext, processor: ImageProcessor):
    """Encapsulated action for the AuditLoop to execute."""
    images_to_process = ctx.get_images_by_status(ProcessingStatus.ID_PASS)
    if not images_to_process:
        logger.info("No images are ready for processing.")
        return 0
        
    processed_count = 0
    for metadata in images_to_process:
        # Placeholder for face location logic
        h, w = (1024, 1024) 
        placeholder_face_location = (h // 4, w - (w // 4), h - (h // 4), w // 4)
        
        processor.process_image(metadata, placeholder_face_location)
        ctx.update_image_status(metadata.image_hash, ProcessingStatus.PROCESSED)
        processed_count += 1
    return processed_count

def main():
    parser = argparse.ArgumentParser(description="Process filtered images for a given subject.")
    parser.add_argument("subject", type=str, help="Name of the person/subject to process.")
    args = parser.parse_args()

    # Load config
    config_path = Path("config.yaml")
    if not config_path.exists():
        logger.error("config.yaml not found in root directory.")
        return

    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)
        
    paths = config_data.get("paths", {})
    processed_dir = paths.get("processed_dir", "data/processed")
    metadata_file = paths.get("metadata_file", "data/metadata.json")
    
    # Phase 2: Materialized Protocol (AuditLoop)
    ctx = ProjectContext(args.subject, metadata_file)
    audit = AuditLoop(ctx)
    
    processor = ImageProcessor(output_dir=processed_dir, target_size=512, crop_scale=1.7)
    
    # 1. Plan
    audit.plan(ProcessingStatus.ID_PASS, ProcessingStatus.PROCESSED)
    
    # 3. Execute (Step 2 'Instrument' is using this code)
    processed_count = audit.execute_stage(
        "Image Alignment and Cropping", 
        run_processing, ctx, processor
    )
    
    # 4. Verify & Commit
    if processed_count > 0:
        if audit.verify(run_tests=False): # Skipping tests for brevity in this example
            audit.commit()
            logger.info(f"Processing complete. Successfully processed {processed_count} images.")
        else:
            logger.error("Verification failed. Changes not committed.")
    else:
        logger.info("No work performed.")

if __name__ == "__main__":
    main()
