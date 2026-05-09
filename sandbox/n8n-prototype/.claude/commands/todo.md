Scan the following PARA directories for all action items:
- 01_Projects/
- 02_Areas/
- 03_Resources/
- backlog/

Search for:
- Lines starting with `- [ ]` (unchecked Markdown checkboxes)
- Lines containing `TODO:`, `FIXME:`, or `ACTION:`
- Any file in `backlog/` that appears stale (check its content for deferred tasks)

Output format:

## 🔴 Urgent (due today or overdue)
## 🟡 This Week
## 🟢 Backlog / Parked

Group items by source file. Include the relative file path for each group.
If no items found, say so clearly.
