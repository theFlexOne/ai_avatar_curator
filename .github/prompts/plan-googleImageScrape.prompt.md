## Plan: Google Image Search & Scrape Implementation

Implement a robust, asynchronous Google Image scraper using SerpApi. The scraper will fetch image metadata, download images concurrently, deduplicate via hashing, and store everything with proper metadata as defined in the project's schemas.

**Steps**

### Phase 1: Foundation & Base Classes
1. **Define Base Interface**: Create `src/scrapers/base.py` with an abstract `BaseScraper` class. This ensures all scrapers (Google, Yandex, Bing) return `ScrapedImageResult` objects consistently.
2. **Implement Async Downloader**: Create `src/scrapers/utils.py` containing an `AsyncDownloader` class. This utility will:
    - Use `httpx` or `aiohttp` for concurrent downloads.
    - Generate MD5/SHA-256 hashes for each image (for `ImageMetadata.image_hash`).
    - Handle retries and basic file validation (e.g., checking if the file is an image).

### Phase 2: Google Scraper Implementation
3. **Implement GoogleScraper**: Create `src/scrapers/google_scraper.py` using SerpApi.
    - Use `httpx.AsyncClient` to call the SerpApi REST API directly.
    - Support specialized parameters for headshots: `imgsz='l'` (large), `imgar='s'` (square), and `itp='face'`.
    - Map SerpApi's `images_results` to the `ScrapedImageResult` Pydantic model.
4. **Implement Reverse Image Search**: Add a method to `GoogleScraper` to support `google_reverse_image` or `google_lens` when a reference image URL is provided.

### Phase 3: Integration & Persistence
5. **Orchestration Logic**: Create `src/scrapers/manager.py` (or update `src/scrapers/__init__.py`) to coordinate search and download phases.
    - It will take a `SearchConfig`, call the appropriate scrapers, and then trigger the `AsyncDownloader`.
6. **Metadata Persistence**: Implement logic to update `data/metadata.json` using the `ProjectState` model after downloads are complete. This involves converting `ScrapedImageResult` + downloaded file info into `ImageMetadata`.
7. **CLI Entry Point**: Create a script `src/scrape.py` or add a `Makefile` target to trigger a scrape using the person's name and query from `config.yaml`.

**Relevant files**
- `src/schemas.py` — Reuse `ScrapedImageResult`, `ImageMetadata`, and `ImageSource`.
- `src/scrapers/base.py` — New: Abstract base class for all scrapers.
- `src/scrapers/google_scraper.py` — New: SerpApi implementation.
- `src/scrapers/utils.py` — New: Hashing and `AsyncDownloader`.
- `config.yaml` — Read `search` and `paths` settings.
- `requirements.txt` — Add `httpx` and `respx` (for testing).

**Verification**
1. **Unit Test**: Validate the mapping from SerpApi JSON to `ScrapedImageResult`.
2. **Mocked Integration**: Use `respx` to mock SerpApi responses and verify the `GoogleScraper` logic without hitting the real API.
3. **Functional Test**: Run a limited scrape (e.g., 5 results) for a dummy name and verify images appear in `data/raw/` with a corresponding entry in `metadata.json`.

**Decisions**
- **Library**: Use `httpx` instead of the official SerpApi library to benefit from better async support and integration with the rest of the pipeline.
- **Handoff**: Implementation of Yandex and Bing scrapers is excluded from this specific plan but the base class will make them easy to add later.

**Further Considerations**
1. **API Key Safety**: Ensure the scraper reads `SERPAPI_API_KEY` from environment variables (using `python-dotenv`) as per `rules.md`.
2. **Concurrency**: Default `download_concurrency` to 5 (from `config.yaml`) to avoid being flagged by host sites during bulk downloads.