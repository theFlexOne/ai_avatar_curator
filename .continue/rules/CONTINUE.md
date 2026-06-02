# AI Avatar Curator - Project Guide

## Project Overview
The **AI Avatar Curator** is a specialized tool designed to automate the creation of high-quality facial datasets for training AI models (e.g., LoRA, Dreambooth, Flux). It streamlines the process of searching, downloading, filtering, and processing images of a specific subject.

### Key Technologies
- **Language:** Python 3.10+
- **Image Processing:** OpenCV, Pillow, NumPy
- **Asynchronous I/O:** `aiohttp`, `httpx`, `playwright`
- **Data Validation:** `Pydantic`
- **Dashboard:** `Streamlit`
- **Quality Control:** `Ruff` (linting), `Pytest` (testing)

### High-Level Architecture
The project follows a pipeline-based architecture orchestrated by `src/pipeline.py`.
1. **Scraping (`src/scrapers/`):** Acquires raw images from various web sources.
2. **Filtering (`src/filters/`):** Performs basic quality checks (resolution, sharpness) and advanced face analysis (detection, recognition, occlusion check).
3. **Processing (`src/processors/`):** Normalizes, crops, and aligns faces for training.
4. **State Management (`src/context.py` & `src/schemas.py`):** Tracks every image through a strict state machine (`ProcessingStatus`).

---

## Getting Started

### Prerequisites
- Python 3.10 or higher
- `make` (for automation)
- API keys for search engines (if applicable, configured in `.env`)

### Installation
1. Clone the repository.
2. Run `make setup` to create a virtual environment and install dependencies.
3. Copy `.env.example` to `.env` and fill in the required environment variables.

### Basic Usage
To start a curation pipeline for a subject:
```bash
# Scrape images for a subject
make scrape SUBJECT="John Doe"

# Process scraped images
make process SUBJECT="John Doe"

# Launch the review UI
make ui
```

### Running Tests
```bash
make test
make lint
```

---

## Project Structure
- `src/`: Core source code.
  - `schemas.py`: Pydantic models defining the data domain (the "Source of Truth").
  - `context.py`: Handles persistence and state of the curation project.
  - `audit.py`: Implements the "Audit Loop" protocol for safe state transitions.
  - `scrapers/`: Modules for different image sources.
  - `filters/`: Logic for quality and face filtering.
  - `processors/`: Image manipulation and alignment.
  - `ui/`: Streamlit-based human-in-the-loop validation tool.
- `data/`: Local storage (ignored by Git).
  - `raw/`: **Immutable** original downloads.
  - `processed/`: Final aligned and cropped images.
- `docs/`: Additional documentation and agent protocols.
- `scripts/`: Utility scripts (e.g., enforcing read-only raw data).

---

## Development Workflow

### The Audit Loop Protocol
When implementing new features or modifying the pipeline, follow the **Audit Loop**:
1. **Plan**: Define the `ProcessingStatus` transition.
2. **Instrument**: Ensure metadata schema supports necessary fields.
3. **Execute**: Implement the transformation logic.
4. **Verify**: Run `make test` and validate that invariants hold (e.g., processed images must have face metrics).

### Coding Standards
- **Schema First**: Use `src/schemas.py` to define all data structures.
- **Immutability**: Never modify files in `data/raw/`.
- **Typing**: Use type hints for all function signatures.
- **Linting**: Ensure `make lint` passes before committing.

---

## Key Concepts

### ProcessingStatus
Images move through several states:
- `RAW`: Newly downloaded.
- `FILTERED_PASS/FAIL`: Result of basic quality checks.
- `FACE_PASS/FAIL`: Result of face detection.
- `ID_PASS/FAIL`: Result of face recognition (identity check).
- `PROCESSED`: Final state after cropping/alignment.

### Subject Context
A "Project" is centered around a `subject_name`. All metadata is scoped to this subject and persisted in a local JSON state within the `data/` directory.

---

## Common Tasks

### Adding a New Scraper
1. Create a new module in `src/scrapers/`.
2. Inherit from the base scraper class (if applicable).
3. Return `ScrapedImageResult` objects.
4. Register the scraper in `src/scrapers/manager.py`.

### Customizing Filters
1. Add new filter logic in `src/filters/`.
2. Update `FilterStage` in `src/pipeline.py` to include your new check.
3. Ensure failed checks update the metadata status to an appropriate `*_FAIL` state.

---

## Troubleshooting
- **Permission Denied in `data/raw/`**: This directory is intentionally set to read-only to preserve original data. Use `data/processed/` or `data/interim/` for modifications.
- **Missing Dependencies**: Ensure you are inside the virtual environment (`source .venv/bin/activate`).
- **Pydantic Validation Errors**: Check `src/schemas.py` to ensure the incoming data matches the expected format.

---

## References
- [Project Roadmap](README.md#roadmap)
- [Agent Protocols](AGENTS.md)
- [Pydantic Documentation](https://docs.pydantic.dev/)
