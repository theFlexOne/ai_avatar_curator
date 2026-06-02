# AI Avatar Curator

Automated high-quality facial dataset curation for AI avatar training.

## Overview
This project provides tools to search, download, and filter images of a target subject to create a clean, high-resolution dataset for training models like LoRA, Dreambooth, or Flux.

## Getting Started
1. **Setup:** `make setup`
2. **Configure:** Copy `.env.example` to `.env` and add your API keys.
3. **Run:** (Usage instructions coming soon)

## Project Structure
- `data/`: Raw and processed images (ignored by git).
- `src/`: Source code including:
  - `scrapers/`: Search and download modules.
  - `filters/`: Face detection and quality checks.
  - `processors/`: Cropping and normalization.
  - `ui/`: Streamlit dashboard for review.
- `instructions.md`: Detailed AI workflow instructions.
- `rules.md`: Project coding standards.

## License
MIT
