# Architecture & Modules

This document outlines the distinct services, tools, and modules that make up the AI Avatar Curator. Use this as a reference for the project's components and responsibilities.

## 1. Data Acquisition (`src/scrapers/`)
Responsible for fetching raw images and returning them as `ScrapedImageResult` objects.
*   **Static API Scraper:** Uses `requests` and `aiohttp` for structured API fetching (e.g., Unsplash).
*   **Dynamic Web Scraper:** Uses `playwright` for JS-heavy sites (e.g., Pinterest).
*   **Local Ingestor:** Bulk-imports local images.
*   **Rate Limiter / Retry:** Wraps requests to handle HTTP 429 and retries gracefully.

## 2. Quality Control & Analysis (`src/filters/`)
Evaluates images and returns scores/booleans (populating `FaceMetrics`). Does *not* alter image data.
*   **Blur / Sharpness Detector:** `cv2.Laplacian(image, cv2.CV_64F).var()`.
*   **Brightness / Contrast Evaluator:** Analyzes pixel intensity via `numpy`/`cv2`.
*   **Face Validator:** Uses `face_recognition.face_locations()` to ensure exactly *one* face exists.
*   **Duplicate Catcher (Optional):** Perceptual hashing to prevent duplicates.

## 3. Image Manipulation (`src/processors/`)
Physically alters image data to create the final avatar.
*   **Face Extractor & Cropper:** Calculates margins around bounding boxes and slices `numpy` arrays.
*   **Color Space Converter:** Handles OpenCV BGR to RGB conversion.
*   **Resizer & Optimizer:** Normalizes size (e.g., 512x512) and saves optimized JPEG/PNG.

## 4. User Interface (`src/ui/`)
*   **Streamlit Dashboard:** Main `app.py` UI.
*   **Gallery Viewer:** Grid display of processed avatars.
*   **Approval/Labeling Component:** Updates `is_approved` and `tags` fields.
*   **Metrics Sidebar:** UI for adjusting threshold settings dynamically.

## 5. Core Infrastructure & Storage (Root / `src/`)
*   **Schema Manager (`src/schemas.py`):** Single source of truth for Pydantic models.
*   **Configuration Loader:** Parses `config.yaml` and `.env` to provide global settings.
*   **Storage & Metadata Manager:** Manages local file system (`/data/raw/`, `/data/processed/`) and metadata tracking.

## 6. DevTools & Quality Assurance (`tests/` & Root)
*   **Test Fixtures:** Mock `numpy` arrays and static sample images (`tests/fixtures/`).
*   **Makefile Automation:** Commands for pipeline execution (`make scrape`, `make process`, `make ui`).
*   **Linter/Formatter:** `ruff` for strict Python formatting.
