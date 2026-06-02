import asyncio
import hashlib
import logging
from pathlib import Path
from typing import Optional

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

    async def download_image(self, result: ScrapedImageResult) -> Optional[ImageMetadata]:
        """
        Download a single image and return its metadata.
        
        Args:
            result: The scraped image result metadata.
            
        Returns:
            ImageMetadata if successful, None otherwise.
        """
        async with self.semaphore, httpx.AsyncClient(
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
            follow_redirects=True,
            timeout=20.0
        ) as client:
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    url = result.image_url
                    response = await client.get(url)
                    response.raise_for_status()
                    
                    content_type = response.headers.get("Content-Type", "").lower()
                    
                    if "text/html" in content_type:
                        logger.warning(f"Skipping HTML content for {url}")
                        return None

                    if not content_type.startswith("image/"):
                        logger.warning(f"Skipping non-image content ({content_type}) from {url}")
                        return None

                    content = response.content
                    
                    # Basic magic number check for common image formats
                    if not any(content.startswith(magic) for magic in [b"\xff\xd8", b"\x89PNG", b"RIFF"]):
                        logger.warning(f"Content from {url} does not appear to be a valid image (failed magic number check).")
                        return None

                    image_hash = hashlib.md5(content).hexdigest()
                    
                    # Determine extension from content-type or URL
                    ext = self._get_extension(content_type, url)
                    filename = f"{image_hash}{ext}"
                    local_path = self.raw_dir / filename
                    
                    # Save to disk
                    with open(local_path, "wb") as f:
                        f.write(content)
                    
                    return ImageMetadata(
                        image_hash=image_hash,
                        source_url=url,
                        page_url=result.page_url,
                        source=result.source,
                        search_query=result.search_query,
                        title=result.title,
                        original_filename=filename,
                        local_path=str(local_path),
                        status=ProcessingStatus.RAW
                    )
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Retry {attempt + 1} for {result.image_url} due to error: {e}")
                        await asyncio.sleep(1)
                        continue
                    logger.error(f"Failed to download {result.image_url} after {max_retries} attempts: {e}")
                    return None
            return None # Should not reach here if successful

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
