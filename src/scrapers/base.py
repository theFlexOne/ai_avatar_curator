from abc import ABC, abstractmethod
from typing import List
from src.schemas import ScrapedImageResult, SearchConfig

class BaseScraper(ABC):
    """Abstract base class for all image scrapers."""

    @abstractmethod
    async def search(self, config: SearchConfig) -> List[ScrapedImageResult]:
        """
        Perform a search and return a list of image results.
        
        Args:
            config: Configuration for the search operation.
            
        Returns:
            A list of ScrapedImageResult objects.
        """
        pass
