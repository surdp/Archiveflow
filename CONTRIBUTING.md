# Contributing

1. Create a virtual environment if desired (no third-party packages are required).
2. Run the tests from the repository root:

   ```powershell
   $env:PYTHONPATH = "$PWD\src"
   py -3.12 -m unittest discover -s tests -v
   ```

3. Use synthetic or anonymized fixtures. Do not open a pull request containing real social-media exports, personal media, private logs, credentials, or session files.
4. Keep network access and platform login outside the MVP. The project is intentionally an organizer for an export the user already downloaded.
