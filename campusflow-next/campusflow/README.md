# CampusFlow Next

Command-line helpdesk ticket manager for a campus, upgraded for safety and reliability: validated input, follow-up notes, combined search, fuller reports, safe JSON storage, and an in-app understanding quiz.

## Team
- Engineer A (Ticket Safety and Storage): _full name_
- Engineer B (Search, Reporting and CLI): _full name_

## Requirements
Python 3.8+ (standard library only).

## Run
```
python3 main.py
```
Menu: 1 Create, 2 List, 3 View, 4 Assign, 5 Change status, 6 Open work queue, 7 Add note, 8 View notes, 9 Search, 10 Search (sorted by priority), 11 Reports, 12 Understanding check, 13 Reload from file, 14 Exit.

## Tests
```
python3 -m unittest discover -v
```
Covers priority rules, validation (zero/negative/decimal/bool/text users), unchanged-state checks after rejected actions, notes, status workflow, open-only queue, search/AND filters, reports (including empty), save/reload with notes and ID continuity, corrupted JSON and duplicate IDs, CLI retries, and quiz scoring.

## Rules
- **Priority (first match wins):** critical = high urgency AND >=10 users; high = high urgency OR >=10 users; medium = medium urgency OR >=3 users; else low.
- **Status:** open -> in_progress -> resolved. In-progress needs an assignee. Resolved tickets need an explicit reopen (-> open) before assignment or notes.
- **Open work queue:** open tickets only, by priority then ticket number.
- **Notes:** open/in-progress tickets only; author required; message 5-300 characters.
- **Search:** title substring (any case) + optional category/status/priority, all combined with AND.

## Storage
Tickets (with notes) are saved in `tickets.json` in the folder you run from. Files from the previous version still load (notes default to empty). A malformed or invalid file is rejected with a clear message and nothing is overwritten. To start fresh, delete `tickets.json`. Quiz explanations are saved to `learning-notes.md` (not committed).

## Known limitations / future work
- Single user; no ticket editing or deletion.
- Staff names are free text.

## Links
- Engineer A PR: _link_
- Engineer B PR: _link_
- Baseline: `baseline-check.md`; AI log: `docs/ai-learning-log.md`; decisions: `docs/design-decisions.md`
