# ArchiveFlow — Privacy-First Instagram Export Organizer

**A local-first Python tool that turns a downloaded social-media data export into an organized photo/video library.**

> Status: **MVP in progress.** The local ZIP/folder organizer is the first usable milestone. The user's real Instagram export has not been inspected by this project, and no personal media is included in this repository.

## Why I built this

I wanted to gather photos and videos from my own Instagram archive without opening every item manually. The initial experiment exposed a useful engineering lesson: logging in successfully does not mean an unofficial private API can read every archive endpoint. ArchiveFlow therefore focuses on processing a data export obtained through Instagram's official Accounts Center flow.

## What it does

- Scans an official export ZIP directly, without extracting the entire archive first.
- Also supports an already-extracted export folder.
- Finds common image and video formats, then copies them into separate local folders.
- Generates `manifest.csv` with the source path, type, output filename, file size, and SHA-256 hash.
- Includes a dry-run mode so you can preview what would be copied.
- Uses Python's standard library; no Instagram login, password, token, scraping, or third-party package is required.

## What it does not do

- It does not log in to Instagram or connect to Instagram's private APIs.
- It does not bypass authentication, security challenges, or rate limits.
- It does not upload your archive to a server.
- It does not publish or share any of your media.
- It does not promise that every media item or every export format is represented; the export layout can vary.

## Requirements

- Python 3.10 or newer
- Windows, macOS, or Linux

There are no third-party Python dependencies.

## Quick start (Windows PowerShell)

1. Download your information using Instagram's official **Accounts Center → Your information and permissions → Export your information** flow. Choose the account and media/data categories you want.
2. Save the downloaded ZIP somewhere private. Do not put the ZIP inside this Git repository.
3. Open PowerShell in the project folder.
4. Create a virtual environment and install this local package (the install has no third-party dependencies):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

5. Preview the media files in the export:

```powershell
.\.venv\Scripts\python.exe -m archiveflow inspect "C:\Path\To\instagram-export.zip"
```

6. Preview the organization plan without copying files:

```powershell
.\.venv\Scripts\python.exe -m archiveflow organize "C:\Path\To\instagram-export.zip" --output "C:\Users\YourName\Pictures\ArchiveFlow" --dry-run
```

7. Run it without `--dry-run` to copy the detected media and create the manifest:

```powershell
.\.venv\Scripts\python.exe -m archiveflow organize "C:\Path\To\instagram-export.zip" --output "C:\Users\YourName\Pictures\ArchiveFlow"
```

### Output layout

```text
ArchiveFlow/
├── images/
├── videos/
└── manifest.csv
```

The manifest contains paths and hashes, not media contents. Treat it as personal metadata nonetheless, and keep it private if the paths reveal personal information.

## Commands

| Command | Purpose |
|---|---|
| `inspect INPUT` | Count supported media by file extension and estimate total size |
| `organize INPUT --output DEST` | Copy supported media into `images/` and `videos/`, then write `manifest.csv` |
| `organize ... --dry-run` | Print the planned actions without creating output files |

`INPUT` can be a ZIP file or a directory that has already been extracted. Unknown file types are skipped; non-media JSON and HTML are not copied.

## Project story: issue → investigation → workaround

See [the case study](docs/CASE_STUDY.md) for the real troubleshooting timeline, what worked, what failed, and the honest current status. See [the roadmap](docs/ROADMAP.md) for the future web application idea.

## Privacy and security

- Process your own export and follow Instagram's terms and applicable law.
- Never commit your Instagram export, private photos/videos, passwords, two-factor codes, browser cookies, session files, or logs that contain secrets.
- This project intentionally does not need Instagram credentials.
- Keep backups before reorganizing important files. ArchiveFlow copies detected media; it does not delete the input.

## Tests

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Roadmap

- [x] Document the original problem and troubleshooting learnings
- [x] Build a dependency-free local ZIP/folder media organizer
- [x] Add dry-run, inventory, hashing, collision-safe filenames, and tests
- [ ] Test against a real official export after it is downloaded (with private files kept local)
- [ ] Improve metadata mapping after inspecting anonymized sample structure
- [ ] Build an attractive local-first web UI with search, filters, and media previews
- [ ] Consider static deployment only for the interface; private archive files should remain on the user's device

## Sources

- Meta: [Managing information in Accounts Center](https://about.fb.com/news/2023/10/manage-your-information-across-apps/)
- Meta Help Center: [Data scraping and how to protect your information](https://www.facebook.com/help/463983701520800)

## License

MIT. See [LICENSE](LICENSE).
