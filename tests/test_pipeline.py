import pytest
from pathlib import Path
from unittest.mock import patch, AsyncMock

# Import actual classes from the project
from src.scrapers.manager import ScraperManager
from src.schemas import ProjectState, SearchConfig, ScrapedImageResult, ImageMetadata, ProcessingStatus
from src.context import ProjectContext
from datetime import datetime

@pytest.mark.asyncio
async def test_end_to_end_pipeline_smoke_test():
    """
    A smoke test to verify the end-to-end pipeline from search to state update.
    """
    subject_name = "test_subject"
    test_data_path = Path("./data")
    
    # 1. Mock Scraper Results
    mock_scraper_result = [
        ScrapedImageResult(image_url="http://example.com/image1.jpg", source="google")
    ]
    
    # 2. Mock Downloader Results
    mock_downloaded_metadata = [
        ImageMetadata(
            image_hash="dummy_hash_123",
            source_url="http://example.com/image1.jpg",
            source="google",
            original_filename="image1.jpg",
            local_path="data/raw/dummy_hash_123.jpg",
            status=ProcessingStatus.RAW,
            timestamp=datetime.utcnow()
        )
    ]

    # 3. Patch the external dependencies: scraper's search and downloader's download_all
    with patch("src.scrapers.google_scraper.GoogleScraper.search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_scraper_result
        
        with patch("src.scrapers.utils.AsyncDownloader.download_image", new_callable=AsyncMock) as mock_downloader:
            mock_downloader.return_value = mock_downloaded_metadata[0]

            # 4. Initialize dependencies
            config = SearchConfig(query="test query", max_results=1)
            state = ProjectState(subject_name=subject_name)
            manager = ScraperManager(raw_dir=str(test_data_path))

            # 5. Run the pipeline
            final_state = await manager.run(config, state)
            
            # 6. Assertions
            # Ensure the mocks were called as expected
            assert mock_search.call_count == 1
            mock_downloader.assert_called_once()
            
            # Verify that the project state was updated correctly
            assert "dummy_hash_123" in final_state.images
            image_meta = final_state.images["dummy_hash_123"]
            assert image_meta.source_url == "http://example.com/image1.jpg"
            assert image_meta.status == ProcessingStatus.RAW

    print("\nSmoke test for the integrated pipeline passed successfully.")

