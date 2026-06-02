import argparse
import asyncio
import logging
import yaml
from pathlib import Path

from src.schemas import SearchConfig
from src.scrapers.manager import ScraperManager
from src.storage import StorageManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def main():
    parser = argparse.ArgumentParser(description="Scrape images for a given subject.")
    parser.add_argument("subject", type=str, help="Name of the person/subject to curate.")
    parser.add_argument("--query", type=str, help="Specific search query (defaults to subject name).")
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
    
    raw_dir = paths.get("raw_dir", "data/raw")
    metadata_file = paths.get("metadata_file", "data/metadata.json")
    
    concurrency = search_cfg.get("download_concurrency", 5)
    max_results = search_cfg.get("max_results_per_query", 100)
    
    query = args.query if args.query else args.subject
    config = SearchConfig(query=query, max_results=max_results)
    
    # Initialize components
    logger.info(f"Initializing scraping for subject: {args.subject}")
    storage = StorageManager(metadata_file)
    state = storage.load_state(args.subject)
    
    manager = ScraperManager(raw_dir=raw_dir, concurrency=concurrency)
    
    # Run pipeline
    state = await manager.run(config, state)
    
    # Persist state
    storage.save_state(state)
    logger.info("Scraping completed and state saved to metadata.")

if __name__ == "__main__":
    asyncio.run(main())
