# ADR 0001: Pipeline State Machine

## Status
Accepted

## Context
The image curation process involves multiple asynchronous and conditional steps (scraping, basic filtering, face detection, identity verification). We need a consistent way to track progress and filter out low-quality data without losing the source records.

## Decision
We implement a formal state machine via the `ProcessingStatus` enum in `src/schemas.py`.

States:
1. `RAW`: Initial state after download.
2. `FILTERED_PASS/FAIL`: Result of basic image quality checks (sharpness, etc.).
3. `FACE_PASS/FAIL`: Result of face detection and landmarking.
4. `ID_PASS/FAIL`: Result of identity verification against a reference photo.
5. `PROCESSED`: Final state after alignment and cropping.

## Consequences
- Every `ImageMetadata` record must have a `status`.
- Filtering logic must update the status rather than deleting the metadata record.
- Processors should only operate on images with a `*_PASS` status.
