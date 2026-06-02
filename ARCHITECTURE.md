# Architecture & Modules

This document outlines the distinct services, tools, and modules that make up the AI Avatar Curator. Use this as a reference for the project's components and responsibilities.

## 1. Data Acquisition (`src/scrapers/` & `src/scrape.py`) - [Phase 2]
Responsible for fetching raw images and returning them as `ScrapedImageResult` objects, then downloading them.
*   **Pipeline Entrypoint (`src/scrape.py`):** CLI script (`make scrape`) that orchestrates reading config, initializing managers, and running the scraping pipeline.
*   **Base Scraper (`src/scrapers/base.py`):** Abstract class defining the `search` interface for all scrapers.
*   **Google Scraper (`src/scrapers/google_scraper.py`):** Uses Google Custom Search API to find image URLs.
*   **Scraper Manager (`src/scrapers/manager.py`):** Coordinates search engines, deduplicates URLs, and updates the `ProjectState`.
*   **Async Downloader (`src/scrapers/utils.py`):** Uses `httpx` and `asyncio` to fetch images concurrently with a semaphore for rate limiting.

## 2. Quality Control & Analysis (`src/filters/`) - [Phase 3]
Evaluates images and returns scores/booleans (populating `FaceMetrics`). Does *not* alter image data.
*   **Blur / Sharpness Detector:** `cv2.Laplacian(image, cv2.CV_64F).var()`.
*   **Brightness / Contrast Evaluator:** Analyzes pixel intensity via `numpy`/`cv2`.
*   **Duplicate Catcher (Optional):** Perceptual hashing to prevent duplicates.

## 3. Face Analysis & AI Recognition (`src/filters/`) - [Phase 4]
Advanced identity-based filtering and pose analysis.
*   **Face Validator:** Uses `face_recognition.face_locations()` to ensure exactly *one* face exists.
*   **Identity Verification:** Compares facial embeddings against a reference photo.
*   **Pose & Occlusion:** Landmark detection for yaw/pitch/roll and occlusion checks.

## 4. Image Manipulation (`src/processors/`) - [Phase 5]
Physically alters image data to create the final avatar.
*   **Face Extractor & Cropper:** Calculates margins around bounding boxes and slices `numpy` arrays.
*   **Color Space Converter:** Handles OpenCV BGR to RGB conversion.
*   **Resizer & Optimizer:** Normalizes size (e.g., 512x512) and saves optimized JPEG/PNG.

## 5. User Interface (`src/ui/`) - [Phase 6]
*   **Streamlit Dashboard:** Main `app.py` UI.
*   **Gallery Viewer:** Grid display of processed avatars.
*   **Approval/Labeling Component:** Updates `is_approved` and `tags` fields.
*   **Metrics Sidebar:** UI for adjusting threshold settings dynamically.

## 6. Core Infrastructure & Storage (Root / `src/`) - [Phase 1]
*   **Schema Manager (`src/schemas.py`):** Single source of truth for Pydantic models (e.g., `ProjectState`, `ImageMetadata`, `ScrapedImageResult`).
*   **Storage Manager (`src/storage.py`):** Serializes and deserializes the `ProjectState` to/from `data/metadata.json`, handling file system state management.
*   **Configuration Loader:** Parses `config.yaml` to provide global settings like paths and API concurrency.

## 7. Agent Infrastructure (`.github/agents/`)
*   **DocSync State (`.github/agents/docsync_state.json`):** Tracks file hashes, audit timestamps, and pending documentation discrepancies. Enables incremental and highly efficient codebase-to-documentation audits.
*   **Custom Agents:** Specialized AI behaviors configured via `.agent.md` files:
    *   **Curator:** The Final Orchestrator. Coordinates all specialized agents through the Audit Loop.
    *   **State Manager:** Progress & State Management. Maintains the `progress_diary.md` and enforces plan-before-code.
    *   **Documentation Aligner:** Documentation & Syncing. Verifies that documentation matches codebase declarations.
    *   **Constraint Enforcer:** Technical Constraints & Data Handling. Verifies execution against schemas and rules.
    *   **Quality Enforcer:** Git & Code Quality Guardrails. Enforces linting, testing, and commit standards.
    *   **Memory Manager:** Memory Maintenance. Owns repository memory and long-term project facts.

## 8. DevTools & Quality Assurance (`tests/` & Root) - [Phase 7]
*   **Test Fixtures:** Mock `numpy` arrays and static sample images (`tests/fixtures/`).
*   **Makefile Automation:** Commands for pipeline execution (`make scrape`, `make process`, `make ui`).
*   **Linter/Formatter:** `ruff` for strict Python formatting.
