# ADR 0003: Schema-Driven Integration

## Status
Accepted

## Context
As the project grows, passing generic dictionaries or arbitrary objects between scrapers, filters, and processors becomes error-prone and hard for agents to navigate.

## Decision
We mandate the use of Pydantic (v2) models defined in `src/schemas.py` for all module communication and persistence.

## Consequences
- `src/schemas.py` is the single source of truth for the domain model.
- All JSON persistence (e.g., `steve_jobs_metadata.json`) must strictly follow the `ProjectState` and `ImageMetadata` schemas.
- Agents must refer to the schema to understand the "interface" between pipeline stages.
