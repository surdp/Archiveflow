# Roadmap

## Phase 1 — CLI MVP

- [x] Scan export ZIP or extracted folder.
- [x] Detect common image/video extensions.
- [x] Count files by type and extension.
- [x] Dry-run preview.
- [x] Organize copies without deleting the source.
- [x] Create a SHA-256 CSV manifest.
- [x] Unit tests using synthetic sample ZIP/folder data.
- [ ] Validate against the user's real official export privately.

## Phase 2 — Export-aware indexing

- Parse documented/exported JSON metadata when its actual format is confirmed.
- Associate filenames with captions and timestamps only when the export provides a reliable mapping.
- Add duplicate review rather than silently deleting anything.
- Add a clearer validation report for unsupported file types and missing media.

## Phase 3 — Local-first web UI

- Drag-and-drop/select ZIP and show a progress indicator.
- Show totals by media type and file extension before export.
- Search/filter media and preview images/videos.
- Let the user choose output organization and download a generated result.
- Keep processing in the browser when practical; never request Instagram credentials.
- Add privacy messaging and an explicit clear/reset action.

## Phase 4 — Portfolio polish

- Add architecture screenshots and an anonymized sample export fixture.
- Add CI tests on Windows and Linux.
- Add a demo using synthetic media only.
- Link the project case study from the personal portfolio after the GitHub repository is published.
