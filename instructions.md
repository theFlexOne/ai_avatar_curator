# AI Usage Instructions: AI Avatar Curator

This document provides specialized instructions for AI agents working on the AI Avatar Curator project. The primary goal is to automate the creation of high-quality facial datasets.

## 1. Data Acquisition Workflow

The goal is to curate a high-quality dataset of a specific person to ensure accurate AI model training.

### 1.1 Search & Retrieval
- **Tools:** Use SerpApi (Google Images), Bing Search API, or specialized social media scrapers.
- **Strategy:**
    - Perform "Advanced Web Search" by combining keywords (e.g., "Person Name headshot", "Person Name interview", "Person Name red carpet").
    - Prioritize high-resolution sources (e.g., photography portfolios, news sites).
    - Handle pagination and rate limiting to avoid blocks.
    - Log search queries and result counts for reproducibility.

### 1.2 Bulk Processing
- **Asynchronous Downloading:** Use `aiohttp` or `httpx` for fast concurrent downloads.
- **Hashing:** Generate MD5/SHA-256 hashes for every downloaded image to prevent duplicates.
- **Directory Structure:**
    - `data/raw/`: Original, untouched downloads.
    - `data/interim/`: Images after basic filtering (e.g., resolution/format).
    - `data/processed/`: Final, high-quality, cropped, and aligned dataset.
- **Metadata:** Store image source URL, timestamp, and original filename in a `metadata.json` file.

### 1.3 Filtering & Quality Assessment
- **Facial Recognition:**
    - Use `face_recognition` or `Mediapipe` to detect faces.
    - Discard images with multiple faces or no faces.
    - Validate that the detected face matches the target subject using a reference embedding.
- **Sharpness Check:**
    - Calculate the Laplacian variance (OpenCV).
    - Threshold: Discard images with a variance below a configurable limit (e.g., 100).
- **Occlusion & Pose:**
    - Use landmark detection to ensure the face is mostly frontal (yaw/pitch/roll within bounds).
    - Discard images where eyes or mouth are significantly occluded.
- **Resolution:** Minimum face size should be 224x224 pixels or higher depending on the target model.

## 2. Implementation Guidelines for AI
- **Code Style:** Prefer Python 3.10+ features (type hints, f-strings, pathlib).
- **Modularity:** Separate the scraper, the filter, and the processor into distinct modules.
- **Error Handling:** Implement robust retries for network requests and graceful failure for corrupted images.
- **Logging:** Use the `logging` module to track progress and filter reasons.
