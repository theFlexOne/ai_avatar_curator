import os
from typing import List, Optional
import httpx
from src.schemas import ScrapedImageResult, SearchConfig, ImageSource
from src.scrapers.base import BaseScraper
import logging

logger = logging.getLogger(__name__)

class GoogleScraper(BaseScraper):
    """Scraper implementation for Google Images using SerpApi."""

    BASE_URL = "https://serpapi.com/search"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_API_KEY must be provided or set in environment.")

    async def search(self, config: SearchConfig) -> List[ScrapedImageResult]:
        """
        Perform a Google Images search via SerpApi, handling pagination.
        If reference images are provided, it also attempts a Google Lens search.
        """
        all_results = []
        
        if config.reference_images and config.offset == 0:
            logger.info("Reference images provided, attempting Google Lens search first.")
            lens_results = await self.lens_search(config.reference_images[0], config.max_results)
            all_results.extend(lens_results)
            logger.info(f"Google Lens found {len(lens_results)} matches.")

        page_num = config.offset
        
        async with httpx.AsyncClient() as client:
            while len(all_results) < config.max_results:
                params = {
                    "engine": "google_images",
                    "q": config.query,
                    "api_key": self.api_key,
                    "ijn": page_num,
                    # Specialized parameters for headshots
                    "imgsz": "qsvga",
                    "itp": "photo",
                }
                
                logger.debug(f"Requesting URL: {self.BASE_URL} with params: {params}")
                response = await client.get(self.BASE_URL, params=params)
                
                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError as e:
                    logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
                    break  # Exit loop on error

                data = response.json()
                logger.debug(f"Received API response with keys: {data.keys()}")

                results = data.get("images_results", [])
                if not results:
                    # No more results, break the loop
                    break
                
                all_results.extend(results)
                
                # Check if there is a next page
                if "serpapi_pagination" not in data or "next" not in data["serpapi_pagination"]:
                    break
                    
                page_num += 1

        # Trim results to the exact number requested
        return [
            ScrapedImageResult(
                image_url=item.get("original"),
                source=ImageSource.GOOGLE,
                page_url=item.get("link"),
                title=item.get("title"),
                search_query=config.query,
                expected_width=item.get("original_width"),
                expected_height=item.get("original_height"),
            )
            for item in all_results[:config.max_results]
        ]

    async def reverse_search(self, image_url: str) -> List[ScrapedImageResult]:
        """
        Perform a Google Reverse Image Search (or Lens) via SerpApi.
        """
        params = {
            "engine": "google_reverse_image",
            "image_url": image_url,
            "api_key": self.api_key,
        }

        async with httpx.AsyncClient() as client:
            logger.debug(f"Requesting URL: {self.BASE_URL} with params: {params}")
            response = await client.get(self.BASE_URL, params=params)
            
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
                raise

            data = response.json()
            logger.debug(f"Received API response with keys: {data.keys()}")

        results = data.get("image_results", [])
        return [
            ScrapedImageResult(
                image_url=item.get("original"),
                source=ImageSource.GOOGLE,
                page_url=item.get("link"),
                title=item.get("title"),
                search_query=f"reverse_search:{image_url}",
            )
            for item in results
        ]

    async def lens_search(self, image_path: str, max_results: int = 10) -> List[ScrapedImageResult]:
        """
        Perform a Google Lens search using a local file upload.
        """
        if not os.path.exists(image_path):
            logger.error(f"Lens search failed: Image path {image_path} does not exist.")
            return []

        # Use .json endpoint as it's more explicit for SerpApi
        endpoint = "https://serpapi.com/search.json"

        async with httpx.AsyncClient() as client:
            with open(image_path, "rb") as f:
                files = {"file": f}
                params = {
                    "engine": "google_lens",
                    "api_key": self.api_key,
                }
                logger.info(f"Uploading {image_path} for Google Lens search...")
                response = await client.post(endpoint, params=params, files=files, timeout=30.0)
                
                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError as e:
                    logger.error(f"Lens search HTTP error: {e.response.status_code} - {e.response.text}")
                    return []

                data = response.json()
                
            results = data.get("visual_matches", [])
            return [
                ScrapedImageResult(
                    image_url=item.get("thumbnail"), # Lens returns thumbnails mainly
                    source=ImageSource.GOOGLE,
                    page_url=item.get("link"),
                    title=item.get("title"),
                    search_query=f"lens_search:{image_path}",
                )
                for item in results[:max_results]
            ]
