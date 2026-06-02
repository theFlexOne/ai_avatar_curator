import os
from typing import List, Optional
import httpx
from src.schemas import ScrapedImageResult, SearchConfig, ImageSource
from src.scrapers.base import BaseScraper
from dotenv import load_dotenv

load_dotenv()

class GoogleScraper(BaseScraper):
    """Scraper implementation for Google Images using SerpApi."""

    BASE_URL = "https://serpapi.com/search"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_API_KEY must be provided or set in environment.")

    async def search(self, config: SearchConfig) -> List[ScrapedImageResult]:
        """
        Perform a Google Images search via SerpApi.
        """
        params = {
            "engine": "google_images",
            "q": config.query,
            "api_key": self.api_key,
            "num": config.max_results,
            # Specialized parameters for headshots
            "imgsz": "l",      # Large images
            "imgar": "s",      # Square aspect ratio
            "itp": "face",     # Face/Portrait filter
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

        results = data.get("images_results", [])
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
            for item in results
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
            response = await client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

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
