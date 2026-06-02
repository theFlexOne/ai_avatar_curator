---
name: progress-tracker
description: 'Generates a formatted display of project progress from progress_diary.md. Shows detailed recent updates and a summarized list of older milestones. Use when asked for "progress", "updates", or "what has been done".'
user-invocable: true
---

# Progress Report

## When to Use
- When the user asks for a project status update or "where do we stand".
- To provide a high-level summary of the main project phases.
- To highlight completed work versus upcoming milestones.

## Procedure

1. **Read Main State**: Open `progress_diary.md` and `instructions.md` (Project Phases).
2. **Read Secondary Context**: Check `/memories/session/plan.md` for any active secondary plans.
3. **Generate Main Report**:
   - **Current Standing**: Identify the current phase based on the latest entries in `progress_diary.md`.
   - **Recent Achievements**: Summarize the 3-5 most recent bullets from the diary.
   - **Phase Progress**: List all project phases from `instructions.md`, marking them as 🟢 (Completed), 🟡 (In Progress), or ⚪ (Not Started).
4. **Generate Secondary Plans Summary**:
   - If `/memories/session/plan.md` exists, list the active goals/tasks in a shortened format.
5. **Display Output**:
   - Use the structure below.

## Example Display Structure

### 📈 Project Progress Report
**Current Phase:** [Phase Number] - [Phase Name] (e.g. 🟡 In Progress)

**Recent Milestones:**
- [Achievement 1]
- [Achievement 2]

**Main Roadmap:**
- 🟢 Phase 1: Project Scaffolding
- 🟡 Phase 2: Data Acquisition
- ⚪ Phase 3: Quality Control
- ... [rest of phases]

---
### 🗒️ Active Secondary Plans
- **[Plan Title]**: [Brief Summary of remaining tasks]
