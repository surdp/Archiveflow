# Case Study: From Manual Archive Download to a Local-First Organizer

## 1. The problem

I wanted to collect my own archived Instagram Stories, posts, photos, and videos for a travel portfolio without opening and saving each item individually. A convenient automated workflow would reduce repetitive effort, but the first approach introduced account-security and API-reliability risks.

## 2. What happened and how we investigated it

| Stage | Observation | What it taught us |
|---|---|---|
| Initial setup | Python was not available from the terminal at first. | Confirm the interpreter installation and PATH before debugging application code. |
| Windows launcher | The batch file stopped with `... was unexpected at this time.` | Treat launcher syntax errors separately from Python or dependency failures. |
| Workaround | Created a virtual environment directly from PowerShell and installed the dependency. | Running commands explicitly made the setup failure easier to isolate. |
| Login | The script printed `Login/session validated.` | Authentication succeeded, but this did not prove the archive endpoints were available. |
| Archive inventory | The private API call returned `UnknownError: We're sorry, but something went wrong.` | The precise server-side cause remained unknown; we should not claim the endpoint failure was fixed. Repeated immediate retries could increase account friction. |
| Safer next step | Started downloading account information through Instagram's official Accounts Center export flow. | Prefer a supported data-export route over depending on undocumented private endpoints. |
| Project direction | Build a local organizer that processes the downloaded ZIP. | Keep credentials out of the code, process data on-device, and make the workflow reproducible. |

## 3. What we overcame

- Installed Python 3.12 and verified that `python`/`py` could run.
- Isolated package dependencies in a project-specific virtual environment.
- Bypassed the faulty Windows batch launcher by running the environment and script commands directly in PowerShell.
- Confirmed that login validation and archive inventory retrieval are different failure points.
- Changed the product approach from account automation to local processing of the official data export.

## 4. What is resolved, and what is not

### Resolved

- Python environment creation.
- Dependency installation.
- Running the script from PowerShell.
- Successful login/session validation for the experimental private-API approach.
- A safer product direction that does not need Instagram credentials.

### Not yet verified

- The exact cause of the generic private-API `UnknownError`.
- The completeness and structure of the user's current official export.
- Whether every archive item is included in the export selected by the user.
- End-to-end processing against a real export. The real export is private and must be tested locally, not committed to GitHub.

## 5. Proposed solution

ArchiveFlow reads an export ZIP or an extracted folder on the user's computer, detects common image/video extensions, copies matching files into separate folders, and writes a CSV manifest including file sizes and SHA-256 checksums. It deliberately does not log in to Instagram or upload files.

## 6. Pros and cons

### Pros

- No Instagram password, 2FA code, session cookie, or API token is required by ArchiveFlow.
- Local processing means private photos and videos do not need to be uploaded to a project server.
- Standard-library-only MVP; minimal setup and fewer dependency risks.
- Dry-run mode previews actions before writing output.
- Manifest supports auditability, inventory, and future gallery/index features.
- The project demonstrates troubleshooting, requirements analysis, privacy-by-design, CLI automation, and test-driven development.

### Cons / limitations

- The user must first request and download the official export; ArchiveFlow does not make that step instantaneous.
- Export categories and folder structures may change or vary by account, language, and export settings.
- Current extension-based detection may miss uncommon formats or items represented only through metadata.
- The MVP copies media but does not reconstruct Story timelines, captions, tags, or original Instagram ordering.
- Same-content files are reported by hashes but are not automatically deduplicated.
- The current CLI is less approachable than a polished browser interface.

## 7. Security decisions

- No credentials are requested or stored by the current project.
- No personal archive, screenshot, export ZIP, session file, or private media belongs in Git.
- Keep exports and generated manifests local; even a CSV can contain personal paths or private filenames.
- A future hosted site should process in the browser or through a user-controlled local service. It should not upload or retain private exports by default.

## 8. What success will look like

After the official ZIP finishes downloading, test it locally: inspect counts, run a dry-run, organize a copy, compare sample outputs with the source, and review the manifest. Only after those checks should the case study state that end-to-end export processing has been validated.
