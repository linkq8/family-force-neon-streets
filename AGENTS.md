# Codex project instructions

The canonical cross-agent project memory is `PROJECT_HISTORY_AR.md`.

For every Codex task in this repository:

1. Before planning or editing, read `PROJECT_HISTORY_AR.md`, then inspect
   `git status --short` and `git log -5 --oneline`.
2. Record the user's new request in the shared log using its template and mark
   it `قيد التنفيذ` before material code or asset changes.
3. On completion or blockage, update that same entry with exact files, tests,
   results, release details, remaining risks, and the next recommended action.
4. Keep the mutable "حالة العمل الحالية" and "تسليم العمل الحالي" sections
   accurate. Do not delete or silently rewrite past entries from Claude Code.
5. Never place secrets, signing passwords, raw customer photos, or sensitive
   personal data in the log.
6. Every new APK release must be pushed to GitHub Releases immediately with
   its tag, direct APK URL, SHA-256, and commit recorded in the shared log.
7. Documentation-only commits do not require a new APK release.
8. If current code or Git evidence conflicts with the log, preserve the old
   entry, add a dated correction, and make the current-state section truthful.

These instructions apply recursively to the whole repository.

