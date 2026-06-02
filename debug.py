import asyncio
from src.schemas import ScrapedImageResult, SearchConfig, ProjectState, ImageSource
from src.scrapers.manager import ScraperManager
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)

async def main():
    raw_dir = Path("./test_raw")
    raw_dir.mkdir(exist_ok=True)
    manager = ScraperManager(raw_dir=str(raw_dir), concurrency=2)
    state = ProjectState(subject_name="test")
    config = SearchConfig(query="test", max_results=2)

    manager.scrapers = [] # remove actual Google scraper
    
    mock_results = [
        ScrapedImageResult(image_url="https://httpbin.org/image/jpeg", source=ImageSource.GOOGLE),
        ScrapedImageResult(image_url="https://httpbin.org/image/jpeg", source=ImageSource.GOOGLE)
    ]
    
    class MockScraper:
        async def search(self, config):
            return mock_results
            
    manager.scrapers.append(MockScraper())
    
    updated_state = await manager.run(config, state)
    print(updated_state)
    print(list(raw_dir.glob("*.*")))

asyncio.run(main())
