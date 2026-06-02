import logging
import asyncio

from src.schemas import SearchConfig, ScrapedImageResult
from src.context import ProjectContext
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

    async def run(self, config: SearchConfig, ctx: ProjectContext) -> None:
        """
        Runs all active scrapers for the given config, downloads the results,
        deduplicates them, and updates the ProjectContext.
        Continues until config.max_results new images are successfully added or it's impossible.
        """
        target_new = config.max_results
        newly_added_count = 0
        page_offset = 0
        
        while newly_added_count < target_new:
            config.offset = page_offset
            # Request at least a reasonable batch size even if we only need a few more
            # to increase the chance of finding unique ones in one go.
            config.max_results = max(target_new - newly_added_count, 10)
            
            current_batch_results = []
            for scraper in self.scrapers:
                logger.info(f"Running scraper: {scraper.__class__.__name__} (page={page_offset}, limit={config.max_results})")
                try:
                    results = await scraper.search(config)
                    current_batch_results.extend(results)
                except Exception as e:
                    logger.error(f"Error running scraper {scraper.__class__.__name__}: {e}")
            
            if not current_batch_results:
                logger.info("No more results found by any scraper. Stopping.")
                break
                
            unique_urls = set()
            to_download = []
            for res in current_batch_results:
                if res.image_url not in unique_urls:
                    unique_urls.add(res.image_url)
                    already_exists = any(m.source_url == res.image_url for m in ctx.images.values())
                    if not already_exists:
                        to_download.append(res)

            if not to_download:
                logger.info("All images in this batch already exist in context. Paginating...")
                page_offset += 1
                if page_offset > 20: # Higher safety limit for pagination
                    break
                continue

            logger.info(f"Found {len(to_download)} new candidate URLs. Downloading...")
            
            # Limit downloads to only what we need to reach the target
            needed = target_new - newly_added_count
            to_download = to_download[:needed]
            
            # Use a local counter for successful additions in this batch
            batch_success_count = 0
            
            async def download_and_update_state(result: ScrapedImageResult):
                nonlocal batch_success_count
                metadata = await self.downloader.download_image(result)
                if metadata:
                    # Leverage: Use the context to handle deduplication and addition
                    if ctx.add_image(metadata):
                        batch_success_count += 1
                        logger.info(f"Added new image {metadata.image_hash} to context.")
                    else:
                        logger.debug(f"Image {metadata.image_hash} already exists in context by hash.")

            # We only want to download up to what we need
            tasks = [download_and_update_state(res) for res in to_download]
            await asyncio.gather(*tasks)
            
            newly_added_count += batch_success_count
            logger.info(f"Batch completed. Added {batch_success_count} new images. Total newly added: {newly_added_count}/{target_new}")
            
            page_offset += 1
            if page_offset > 20:
                logger.warning("Reached maximum pagination safety limit (20).")
                break

        return state
