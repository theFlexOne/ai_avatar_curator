# AI Usage Instructions: AI Avatar Curator

This document provides specialized instructions for AI agents working on the AI Avatar Curator project. The primary goal is to automate the creation of high-quality facial datasets.

## 1. Data Acquisition Workflow

The data acquisition process is divided into two primary phases:
1. **Initial Aggregation:** A broad, slightly fuzzy search (including reverse image search) to cast a wide net across multiple sources.
2. **Refined Filtering:** Using AI-driven facial recognition combined with human verification to ensure the dataset exclusively contains the target subject.

### 1.1 Search & Retrieval
- **Tools:** Use SerpApi (Google Images, Yandex Images), Bing Search API, and social media platforms (e.g., Instagram, LinkedIn).
- **Strategy:**
    - **Fuzzy & Reverse Search:** Use SerpApi's Yandex and Google engines to perform reverse image searches using reference photos.
    - **Keyword Expansion:** Combine keywords (e.g., "Person Name headshot", "Person Name interview", "Person Name red carpet").
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
- **Facial Recognition & Human Validation:**
    - Use `face_recognition` or `Mediapipe` to detect faces and generate embeddings.
    - Discard images with multiple faces or no faces.
    - **AI Validation:** Automatically compare detected faces against a reference embedding to filter out different individuals.
    - **Human-in-the-Loop:** Implement a verification step (UI or CLI) for manual review of borderline AI scores and final dataset validation.
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
