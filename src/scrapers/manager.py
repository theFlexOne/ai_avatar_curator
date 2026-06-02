import logging
from pathlib import Path

from src.schemas import SearchConfig, ProjectState
from src.scrapers.google_scraper import GoogleScraper
from src.scrapers.utils import AsyncDownloader

logger = logging.getLogger(__name__)

class ScraperManager:
    """Coordinates search engines and the downloader to acquire images."""

    def __init__(self, raw_dir: str, concurrency: int = 5):
        self.raw_dir = raw_dir
        self.downloader = AsyncDownloader(raw_dir=raw_dir, concurrency=concurrency)
        self.scrapers = []
        
        # Initialize scrapers based on config (Google is hardcoded for now)
        try:
            self.scrapers.append(GoogleScraper())
        except ValueError as e:
            logger.warning(f"Failed to initialize GoogleScraper (is API key set?): {e}")

    async def run(self, config: SearchConfig, state: ProjectState) -> ProjectState:
        """
        Runs all active scrapers for the given config, downloads the results,
        deduplicates them, and updates the ProjectState.
        """
        all_results = []
        for scraper in self.scrapers:
            logger.info(f"Running scraper: {scraper.__class__.__name__} with query: '{config.query}'")
            try:
                results = await scraper.search(config)
                all_results.extend(results)
                logger.info(f"Found {len(results)} image URLs.")
            except Exception as e:
                logger.error(f"Error running scraper {scraper.__class__.__name__}: {e}")
        
        # Deduplicate URLs before downloading to save bandwidth
        unique_urls = set()
        to_download = []
        for res in all_results:
            if res.image_url not in unique_urls:
                # Basic check if we already have it from source_url in state
                already_exists = any(m.source_url == res.image_url for m in state.images.values())
                if not already_exists:
                    unique_urls.add(res.image_url)
                    to_download.append(res)
        
        logger.info(f"Downloading {len(to_download)} new images...")
        downloaded_metadata = await self.downloader.download_all(to_download)
        
        # Add to state, checking hash duplication (true image identity)
        new_count = 0
        for meta in downloaded_metadata:
            if meta.image_hash not in state.images:
                state.images[meta.image_hash] = meta
                new_count += 1
            else:
                # We already have this exact image, delete the newly downloaded duplicate
                logger.debug(f"Duplicate hash found for {meta.image_url}. Deleting local copy.")
                Path(meta.local_path).unlink(missing_ok=True)
                
        logger.info(f"Added {new_count} new unique images to state.")
        return state
