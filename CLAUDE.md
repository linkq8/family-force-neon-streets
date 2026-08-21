# Claude Code project instructions

Codex and Claude Code share one canonical memory file:
`PROJECT_HISTORY_AR.md`.

For every Claude Code session in this repository:

1. Read `PROJECT_HISTORY_AR.md` completely before proposing or making changes.
2. Also run `git status --short` and `git log -5 --oneline`; do not assume the
   previous session belonged to Claude Code.
3. Add the user's request to "سجل الطلبات والتعديلات المشترك" with executor
   `Claude Code` and status `قيد التنفيذ` before material implementation.
4. When finished or blocked, update the same entry with changed paths, exact
   commands/tests and PASS/FAIL/SKIPPED results, release information, risks,
   and the next action.
5. Update "حالة العمل الحالية" and "تسليم العمل الحالي" before ending the
   session so Codex can continue without needing the Claude conversation.
6. Never delete Codex entries or silently revise history. Add a dated
   correction when evidence conflicts.
7. Never record secrets, keystore credentials, raw customer photos, or other
   sensitive personal data.
8. Every new APK version/release must be uploaded to GitHub Releases and its
   tag, APK URL, SHA-256, and commit must be written to the shared log.
9. A documentation-only change does not require a new APK release.

If a task is already marked `قيد التنفيذ` by another agent, inspect its handoff
and working tree before touching overlapping files.

