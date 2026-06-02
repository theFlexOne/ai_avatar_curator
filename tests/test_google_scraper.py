import pytest
import respx
from src.scrapers.google_scraper import GoogleScraper
from src.schemas import SearchConfig, ImageSource

@pytest.mark.asyncio
async def test_google_scraper_search_mapping():
    scraper = GoogleScraper(api_key="fake_key")
    config = SearchConfig(query="test person", max_results=1)
    
    mock_response = {
        "images_results": [
            {
                "original": "https://example.com/image.jpg",
                "link": "https://example.com/page",
                "title": "Example Image",
                "original_width": 1000,
                "original_height": 1000
            }
        ]
    }
    
    with respx.mock:
        respx.get(scraper.BASE_URL).respond(json=mock_response)
        results = await scraper.search(config)
        
        assert len(results) == 1
        res = results[0]
        assert res.image_url == "https://example.com/image.jpg"
        assert res.source == ImageSource.GOOGLE
        assert res.page_url == "https://example.com/page"
        assert res.title == "Example Image"
        assert res.expected_width == 1000
        assert res.expected_height == 1000

@pytest.mark.asyncio
async def test_google_scraper_reverse_search_mapping():
    scraper = GoogleScraper(api_key="fake_key")
    image_url = "https://example.com/ref.jpg"
    
    mock_response = {
        "image_results": [
            {
                "original": "https://example.com/match.jpg",
                "link": "https://example.com/match_page",
                "title": "Match Image"
            }
        ]
    }
    
    with respx.mock:
        respx.get(scraper.BASE_URL).respond(json=mock_response)
        results = await scraper.reverse_search(image_url)
        
        assert len(results) == 1
        res = results[0]
        assert res.image_url == "https://example.com/match.jpg"
        assert res.search_query == f"reverse_search:{image_url}"
