---
name: progress-tracker
description: 'Generates a formatted display of project progress from progress_diary.md. Shows detailed recent updates and a summarized list of older milestones. Use when asked for "progress", "updates", or "what has been done".'
user-invocable: true
---

# Progress Tracker

## When to Use
- When the user asks for a status update.
- To summarize recent achievements versus long-term history.
- When generating reports on project health.

## Procedure

1. **Read Log**: Open `progress_diary.md` in the workspace root.
2. **Parse Entries**: 
   - Identify entries using `## [Date]: [Phase/Title]` headers.
   - Determine the sort order (chronological or reverse-chronological).
3. **Format Recent Progress**:
   - Identify the latest entry based on date or position (usually the last entry if chronological, first if reverse).
   - For the latest entry, include the header and all descriptive bullet points.
4. **Format Older Progress**:
   - For all other entries, list ONLY the headers (Date and Title).
   - Omit the descriptive bullet points.
5. **Display Output**:
   - Present the "Recent Progress" section first with high detail.
   - Present the "Historical Progress" section second as a concise list.
   - Include the "Next Steps" section at the end.

## Example Display Structure

### 🚀 Recent Progress
**[Date]: [Title]**
- [Detail 1]
- [Detail 2]

### 📜 Older Milestones
- [Date]: [Title]
- [Date]: [Title]
