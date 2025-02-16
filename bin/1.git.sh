#!/bin/bash

# Exit on error
set -e

# run from Documents

# Hardcoded directory containing documents to push
TARGET_DIR="/Users/mymac/Desktop/captions"

# Repository Name
REPO_NAME="captions"

# PAT file location
PAT_FILE="/Users/mymac/Desktop/git_pat.json"

# Log file desktop
LOG_FILE="/Users/mymac/Desktop/backup.log"

# Check if the PAT file exists and is readable
if [ ! -f "$PAT_FILE" ]; then
    echo "PAT file not found at $PAT_FILE. Please ensure it exists."
    exit 1
elif [ ! -r "$PAT_FILE" ]; then
    echo "PAT file at $PAT_FILE is not readable. Please check permissions."
    exit 1
fi

# Verify PAT by making a request to GitHub
echo "Verifying Personal Access Token (PAT)..."
GITHUB_PAT=$(cat "$PAT_FILE")
MASKED_PAT="${GITHUB_PAT:0:4}************"
echo "Using PAT: $MASKED_PAT (masked for security)"
GITHUB_USERNAME="PerlGonzales"

if ! curl -u "$GITHUB_USERNAME:$GITHUB_PAT" https://api.github.com/user &> /dev/null; then
    echo "Invalid or expired PAT. Please generate a new token and update $PAT_FILE."
    exit 1
else
    echo "PAT verified successfully."
fi

# Navigate to the target directory
cd "$TARGET_DIR" || { echo "Directory $TARGET_DIR not found!"; exit 1; }

# Create or append to the log file
echo "Backup script executed on $(date)" >> "$LOG_FILE"

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install Git and try again."
    exit 1
fi

# Check if the directory is already a Git repository
if [ ! -d ".git" ]; then
    echo "Initializing a new Git repository..."
    git init
    echo "Initialized new Git repository in $TARGET_DIR" >> "$LOG_FILE"
else
    echo "Git repository already exists in this directory."
fi

# Set Git user information (global only if not set)
if ! git config --global user.email &> /dev/null; then
    git config --global user.email "perlgonzales72@gmail.com"
fi
if ! git config --global user.name &> /dev/null; then
    git config --global user.name "@PerlGonzales"
fi

# Stage files from MANIFEST or fallback to adding everything
if [ -f MANIFEST ]; then
    echo "Staging files from MANIFEST..."
    while IFS= read -r file; do
        if [ -f "$file" ] || [ -d "$file" ]; then
            git add "$file"
        else
            echo "Warning: $file not found, skipping."
            echo "Warning: $file not found, skipping." >> "$LOG_FILE"
        fi
    done < MANIFEST
else
    echo "MANIFEST not found. Adding all files..."
    git add *
fi

# Check if remote 'origin' exists; if not, add it
if ! git remote | grep -q origin; then
    echo "Remote 'origin' does not exist. Adding it..."
    git remote add origin "https://$GITHUB_USERNAME:$GITHUB_PAT@github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    echo "Added remote 'origin' to repository" >> "$LOG_FILE"
else
    echo "Remote 'origin' already exists."
fi

# Create a verbose, descriptive commit message based on staged changes
who=$(whoami)
now=$(date)
file_list=$(git diff --cached --name-only | tr '\n' ', ' | sed 's/, $//')

# Commit all staged changes
if git diff --cached --quiet; then
    echo "No changes to commit."
    echo "No changes to commit on $now by $who" >> "$LOG_FILE"
else
    git commit -m "On $now, $who added changes in files: $file_list" || { echo "Failed to commit changes"; exit 1; }
    echo "Committed changes: $file_list" >> "$LOG_FILE"
fi

# Push changes to the main branch
git branch -M main
if git push -u origin main; then
    echo "Changes pushed successfully to GitHub."
    echo "Changes pushed successfully on $now by $who" >> "$LOG_FILE"
else
    echo "Failed to push changes. Check network connectivity and repository settings."
    echo "Failed to push changes on $now by $who" >> "$LOG_FILE"
    exit 1
fi

echo "Script completed successfully."
echo "Backup completed on $now" >> "$LOG_FILE"
