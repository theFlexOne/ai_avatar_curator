import asyncio
import hashlib
import logging
from pathlib import Path
from typing import List, Optional

import httpx
from src.schemas import ScrapedImageResult, ImageMetadata, ProcessingStatus

logger = logging.getLogger(__name__)

class AsyncDownloader:
    """Utility class for downloading images asynchronously."""

    def __init__(self, raw_dir: str, concurrency: int = 5):
        self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.concurrency = concurrency
        self.semaphore = asyncio.Semaphore(concurrency)

    async def download_image(
        self, 
        result: ScrapedImageResult, 
        client: httpx.AsyncClient,
        retries: int = 3
    ) -> Optional[ImageMetadata]:
        """
        Download a single image and return its metadata with retry logic.
        
        Args:
            result: The scraped image result metadata.
            client: The HTTP client to use for downloading.
            retries: Number of download attempts.
            
        Returns:
            ImageMetadata if successful, None otherwise.
        """
        async with self.semaphore:
            for attempt in range(retries):
                try:
                    response = await client.get(
                        result.image_url, 
                        timeout=15.0, 
                        follow_redirects=True
                    )
                    response.raise_for_status()
                    
                    content = response.content
                    # Basic validation: Minimum size check (e.g., 1KB)
                    if len(content) < 1024:
                        logger.warning(f"Image too small ({len(content)} bytes): {result.image_url}")
                        return None

                    image_hash = hashlib.md5(content).hexdigest()
                    
                    # Determine extension
                    ext = self._get_extension(response.headers.get("Content-Type"), result.image_url)
                    filename = f"{image_hash}{ext}"
                    local_path = self.raw_dir / filename
                    
                    # Deduplication: check if file already exists
                    if not local_path.exists():
                        with open(local_path, "wb") as f:
                            f.write(content)
                    
                    return ImageMetadata(
                        image_hash=image_hash,
                        source_url=result.image_url,
                        page_url=result.page_url,
                        source=result.source,
                        search_query=result.search_query,
                        title=result.title,
                        original_filename=filename,
                        local_path=str(local_path),
                        status=ProcessingStatus.RAW
                    )
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        logger.error(f"Image not found (404): {result.image_url}")
                        break
                    logger.warning(f"Attempt {attempt + 1} failed for {result.image_url}: {e}")
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {result.image_url}: {e}")
                
                if attempt < retries - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
            
            return None

    def _get_extension(self, content_type: Optional[str], url: str) -> str:
        """Helper to determine file extension."""
        if content_type:
            if "jpeg" in content_type:
                return ".jpg"
            if "png" in content_type:
                return ".png"
            if "webp" in content_type:
                return ".webp"
        
        # Fallback to URL extension
        suffix = Path(url).suffix.split("?")[0].lower()
        if suffix in [".jpg", ".jpeg", ".png", ".webp"]:
            return suffix if suffix != ".jpeg" else ".jpg"
            
        return ".jpg"  # Default

    async def download_all(self, results: List[ScrapedImageResult]) -> List[ImageMetadata]:
        """
        Download a list of images concurrently.
        
        Args:
            results: List of ScrapedImageResult objects.
            
        Returns:
            List of successfully downloaded ImageMetadata objects.
        """
        async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}) as client:
            tasks = [self.download_image(res, client) for res in results]
            downloaded = await asyncio.gather(*tasks)
            return [m for m in downloaded if m is not None]
