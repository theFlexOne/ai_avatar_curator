# AI Avatar Curator: Domain Context

This document defines the domain language and system invariants for the AI Avatar Curator project. All agents must use this vocabulary and adhere to these technical constraints.

## Domain Glossary

| Term | Definition |
| :--- | :--- |
| **Subject** | The target person or entity for whom avatars are being curated (e.g., "Steve Jobs"). |
| **ImageMetadata** | The central Pydantic record for an image, tracking its lifecycle, source, and metrics. |
| **ProcessingStatus** | The state of an image in the pipeline: `RAW`, `FILTERED_PASS/FAIL`, `FACE_PASS/FAIL`, `ID_PASS/FAIL`, `PROCESSED`. |
| **FaceMetrics** | Data extracted during analysis: bounding boxes, sharpness, similarity scores, and landmarks. |
| **CuratedAvatar** | A final, approved image ready for use, linked to its metadata and approval status. |
| **ProjectState** | The root container for a subject's library, metadata, and curation progress. |

## System Architecture

The project implements a multi-stage pipeline designed for high-fidelity avatar curation:

1.  **Data Acquisition**: Orchestrated by `ScraperManager`. Images are fetched, deduplicated via hashing, and stored in `data/raw/`.
2.  **Audit Loop (Filtering)**: 
    *   **Basic Filters**: Rapid checks for resolution, brightness, and global sharpness.
    *   **Face Analysis**: Identity verification and landmark extraction using `face_recognition`.
3.  **Image Processing**: Alignment (rotating eyes to horizontal), square cropping, and normalization.

## Technical Invariants

- **Color Space**: OpenCV defaults to **BGR**. You **MUST** convert to **RGB** before using `face_recognition` or high-level processing modules.
- **Data Tiers**:
    - `data/raw/`: Strictly read-only source data.
    - `data/interim/`: Intermediate results from filters.
    - `data/processed/`: Final aligned and cropped avatars.
- **Schema-Driven**: All data passing between modules must use the Pydantic models defined in `src/schemas.py`.

## Standard Workflows

- `make setup`: Environment and dependency installation.
- `make scrape SUBJECT="Name"`: Run acquisition pipeline.
- `make process SUBJECT="Name"`: Run filtering and processing.
- `make ui`: Launch manual review and curation interface.
- `make test`: Run pytest suite.
- `make lint`: Run ruff checks.
