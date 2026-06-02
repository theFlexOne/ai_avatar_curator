# Progress Diary - AI Avatar Curator

## 2026-06-01: Phase 1 - Project Scaffolding
- Initialized project repository with a structured layout (`src/`, `tests/`, `data/`).
- Created `Makefile` for streamlined environment setup and task execution.
- Defined project-wide `rules.md` and `instructions.md` to guide AI development.
- Set up core configuration management via `config.yaml` and `.env`.
- **Architectural Foundation:** Established modular design in `ARCHITECTURE.md`:
  - `src/scrapers/`: Data acquisition (Static/Dynamic/Local).
  - `src/filters/`: Quality control (Sharpness/Face Validation).
  - `src/processors/`: Image manipulation (Cropping/Normalization).
  - `src/ui/`: Streamlit-based human-in-the-loop validation.
- **Data Integrity:** Initialized `src/schemas.py` with Pydantic models:
  - `ImageSource`, `ProcessingStatus`, `FaceMetrics`, `ImageMetadata`, and `ProjectState`.
  - Enforced strict type hinting and data flow conventions.

## 2026-06-01: Phase 2 - Data Acquisition & Retrieval (Part 1)
- Implemented `GoogleScraper` using SerpApi for high-quality image retrieval.
- Added support for specialized search parameters:
  - `imgsz: l` (Large images)
  - `imgar: s` (Square aspect ratio)
  - `itp: face` (Face/Portrait filter)
- Integrated Google Reverse Image Search capability to expand dataset from reference photos.
- Added unit tests in `tests/test_google_scraper.py` to ensure API response parsing reliability.
- **Noteworthy:** Successfully handled SerpApi's JSON response structure for both standard and reverse searches, mapping them to a unified internal schema.

## 2026-06-01: Phase 2 - Scraper Management & Deduplication
- Implemented `ScraperManager` to coordinate multiple scraping sources.
- Integrated MD5 hashing for content-based deduplication during the aggregation phase.
- Added integration tests in `tests/test_scraper_manager.py` to verify logic for filtering already-seen image URLs and hashes.

## 2026-06-01: Policy Update - Pragmatic Testing
- Refined the "tests along the way" policy to focus on **Pragmatic Testing**.
- Priority is given to essential tests that validate core logic and keep the project on track with the implementation plan.
- Emphasis on key workflows and stability over exhaustive 100% immediate coverage.

---
*Next Steps:*
- Implement asynchronous batch downloading with `aiohttp` (Completing Phase 2).
- Implement basic filtering: sharpness and resolution checks (Phase 3).
- Integrate face detection and embedding comparison (Phase 4).
