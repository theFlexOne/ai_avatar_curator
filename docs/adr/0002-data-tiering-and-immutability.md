# ADR 0002: Data Tiering and Immutability

## Status
Accepted

## Context
To ensure reproducibility and protect source data from accidental corruption during experimentation with filters or processors, we need a strict data management strategy.

## Decision
We adopt a three-tier immutable storage model:

1. **`data/raw/`**: Read-only. Contains original images as downloaded. No script is permitted to modify these files.
2. **`data/interim/`**: Transient. Stores intermediate results or diagnostic images from the Audit Loop.
3. **`data/processed/`**: Final results. Stores the actual cropped/aligned avatars.

Immutability is reinforced by the `scripts/enforce_read_only.py` utility.

## Consequences
- All image operations must treat the raw directory as a source, not a workspace.
- Metadata is stored separately from images to allow state changes without moving source files.
