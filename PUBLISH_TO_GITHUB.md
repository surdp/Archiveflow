# Publish ArchiveFlow to GitHub

Recommended repository name: `archiveflow`.

## 1. Create the repository

On GitHub, choose **New repository**. Name it `archiveflow`, select **Public** for a portfolio project, add a short description such as `A privacy-first local organizer for photos and videos in a downloaded data export`, and do **not** initialize it with a README, license, or `.gitignore` (this folder already has them). Create the repository.

## 2. Push this project from PowerShell

Extract `ArchiveFlow_Project.zip` to a normal folder, open PowerShell in the extracted `ArchiveFlow` folder, and run the commands below. Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username.

```powershell
git --version
git init
git add .
git status
git commit -m "Initial ArchiveFlow local export organizer"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/archiveflow.git
git push -u origin main
```

Check `git status` before committing. It should not list your real Instagram export, private media, `.venv`, session files, passwords, cookies, or `download_errors.txt`. The `.gitignore` is designed to exclude common local artifacts, but always inspect the staged file list.

If Git asks you to configure an author name/email, use:

```powershell
git config --global user.name "Your Name"
git config --global user.email "YOUR_GITHUB_NOREPLY_EMAIL"
```

Use the email configured for your GitHub account; a GitHub-provided noreply address is an option if you prefer not to expose your personal email.

If `git` is not recognized, install Git for Windows from https://git-scm.com/download/win, open a new PowerShell window, and repeat the commands.

## 3. Verify the repository

After `git push` finishes, open `https://github.com/YOUR_GITHUB_USERNAME/archiveflow`. The README should appear on the repository front page.

## 4. Link it from your portfolio later

Once the standalone repository is live and has been tested against a real export, add a project card or case-study link in your portfolio. Do not link a tool as fully production-ready until the real-export test is completed.
