import pytest
import respx
from pathlib import Path
from src.schemas import SearchConfig, ProjectState, ImageSource, ProcessingStatus
from src.scrapers.manager import ScraperManager

@pytest.fixture
def mock_directories(tmp_path):
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    return str(raw_dir)

@pytest.mark.asyncio
async def test_scraper_manager_full_flow(mock_directories):
    raw_dir = mock_directories
    
    manager = ScraperManager(raw_dir=raw_dir, concurrency=2)
    config = SearchConfig(query="test subject", max_results=2)
    state = ProjectState(subject_name="test subject")

    mock_serpapi_response = {
        "images_results": [
            {
                "original": "https://example.com/image1.jpg",
                "link": "https://example.com/page1",
                "title": "Image 1",
            },
            {
                "original": "https://example.com/image2.jpg",
                "link": "https://example.com/page2",
                "title": "Image 2",
            }
        ]
    }
    
    mock_image_bytes = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00\x48\x00\x48\x00\x00' + b'\x00' * 5000 + b'\xff\xd9'

    with respx.mock(assert_all_called=False) as respx_mock:
        respx_mock.get(url__startswith="https://serpapi.com/search").respond(json=mock_serpapi_response)
        respx_mock.get("https://example.com/image1.jpg").respond(content=mock_image_bytes, headers={"Content-Type": "image/jpeg"})
        respx_mock.get("https://example.com/image2.jpg").respond(content=mock_image_bytes, headers={"Content-Type": "image/jpeg"})
        
        updated_state = await manager.run(config, state)
        
        assert len(updated_state.images) == 1
        
        downloaded_files = list(Path(raw_dir).glob("*.*"))
        assert len(downloaded_files) == 1
        
        image_meta = list(updated_state.images.values())[0]
        assert image_meta.source == ImageSource.GOOGLE
        assert image_meta.status == ProcessingStatus.RAW
        assert image_meta.local_path == str(downloaded_files[0])
