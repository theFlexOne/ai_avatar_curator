import argparse
import asyncio
import logging
import yaml
from pathlib import Path
from typing import List
from dotenv import load_dotenv

from src.schemas import SearchConfig, ProcessingStatus
from src.context import ProjectContext
from src.audit import AuditLoop
from src.pipeline import ScrapeStage, FilterStage, AlignStage
from src.scrapers.manager import ScraperManager
from src.processors.image_processor import ImageProcessor

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Note: process_images function is now replaced by FilterStage and AlignStage

async def main():
    """Main function to run the scraping and processing pipeline."""
    load_dotenv()
    parser = argparse.ArgumentParser(description="Scrape and process images for a subject.")
    parser.add_argument("subject", type=str, help="Name of the person/subject to curate.")
    parser.add_argument("--query", type=str, help="Specific search query (defaults to subject name).")
    parser.add_argument("--limit", type=int, help="Override the max_results setting from config.yaml for a limited run.")
    args = parser.parse_args()

    # Load config
    config_path = Path("config.yaml")
    if not config_path.exists():
        logger.error("config.yaml not found in root directory.")
        return

    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)
        
    paths = config_data.get("paths", {})
    search_cfg = config_data.get("search", {})
    
    # Construct paths
    subject_slug = args.subject.lower().replace(" ", "_")
    subject_raw_dir = str(Path(paths.get("raw_dir", "data/raw")) / subject_slug)
    subject_metadata_file = str(Path(paths.get("metadata_file", "data/metadata.json")).parent / f"{subject_slug}_metadata.json")
    processed_dir = str(Path(paths.get("processed_dir", "data/processed")) / subject_slug)
    
    # Initialize Context and Audit Loop
    ctx = ProjectContext(args.subject, subject_metadata_file)
    audit = AuditLoop(ctx)
    
    # Initialize Components
    manager = ScraperManager(raw_dir=subject_raw_dir, concurrency=search_cfg.get("download_concurrency", 5))
    processor = ImageProcessor(
        output_dir=processed_dir,
        target_size=config_data.get("processing", {}).get("target_size", 512),
        crop_scale=config_data.get("processing", {}).get("crop_scale", 1.5)
    )
    
    # Reference images for identity verification
    reference_images = []
    ref_dir = Path("data/reference")
    if ref_dir.exists():
        reference_images = [str(p) for p in ref_dir.glob("*") if p.suffix.lower() in [".jpg", ".jpeg", ".png"]]

    max_results = args.limit if args.limit else search_cfg.get("max_results", 100)
    query = args.query if args.query else args.subject
    search_config = SearchConfig(query=query, max_results=max_results, reference_images=reference_images)
    
    # Run pipeline in a loop
    iteration = 0
    while iteration < 10:
        valid_count = sum(1 for m in ctx.images.values() if m.status in [ProcessingStatus.ID_PASS, ProcessingStatus.PROCESSED])
        if valid_count >= max_results:
            break
            
        # 1. Plan
        audit.plan(ProcessingStatus.RAW, ProcessingStatus.PROCESSED)
        
        # 2. Scrape
        scrape_stage = ScrapeStage(manager, search_config)
        await audit.execute_stage("Scrape", scrape_stage.run, ctx)
        
        # 3. Filter
        filter_stage = FilterStage(config_data, args.subject, reference_images)
        await audit.execute_stage("Filter", filter_stage.run, ctx)
        
        # 4. Align
        align_stage = AlignStage(processor)
        await audit.execute_stage("Align", align_stage.run, ctx)
        
        # 5. Verify & Commit
        if audit.verify(run_tests=False):
            audit.commit()
        else:
            logger.error("Audit verification failed. Breaking loop.")
            break
            
        iteration += 1
        search_config.offset = iteration

    logger.info("Scraping and processing completed.")


if __name__ == "__main__":
    asyncio.run(main())
