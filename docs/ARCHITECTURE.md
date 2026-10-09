# Architecture (MVP)

```text
Official Instagram export ZIP / extracted export folder
                         |
                         v
             Input validation + media scan
                         |
              +----------+----------+
              |                     |
              v                     v
          Image files            Video files
              |                     |
              +----------+----------+
                         v
               Collision-safe copy names
                         |
                         v
             Local output/images and output/videos
                         |
                         v
                   manifest.csv
```

## Design choices

- **Local-only:** all input and output paths are local. There is no network client in the app.
- **Non-destructive:** it copies media and never deletes or modifies the source export.
- **Preview first:** `--dry-run` previews planned operations.
- **Traceability:** each copied file gets a manifest row with source path, category, output path, extension, size, and SHA-256.
- **Path safety:** archive members are treated as names to read and are not extracted directly to arbitrary paths. The output filename is generated from the basename and a short source-path hash.
- **Low dependencies:** uses only Python's standard library.

## Future browser UI

The intended web interface is a local-first organizer, not an Instagram login clone. Preferred design: a static UI that lets a user select a local export file and processes it on-device, with no uploads. If client-side ZIP processing becomes too large or complex, a local-only service bound to `127.0.0.1` is a fallback. A public server should not receive archive ZIPs by default.
