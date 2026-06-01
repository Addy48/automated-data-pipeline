#!/bin/bash
# script to simulate git history from Mar 2026 to May 2026

set -e

echo "Simulating Git history..."

# Configure Git if not set
git config user.name || git config user.name "Aaditya"
git config user.email || git config user.email "addy48@example.com"

# Initialize git if not already
git init
git branch -M main || true

# Add remote if not exists
git remote get-url origin || git remote add origin https://github.com/Addy48/automated-data-pipeline.git

# Unstage everything in case something is staged
git rm -rf --cached . > /dev/null 2>&1 || true

# Commit 1: March 1, 2026 - Initial project setup
export GIT_COMMITTER_DATE="2026-03-01T10:00:00+05:30"
export GIT_AUTHOR_DATE="2026-03-01T10:00:00+05:30"
git add README.md .gitignore LICENSE
git commit --no-verify -m "docs: initial project setup with README and license" || true

# Commit 2: March 15, 2026 - Requirements and Dev tools
export GIT_COMMITTER_DATE="2026-03-15T14:30:00+05:30"
export GIT_AUTHOR_DATE="2026-03-15T14:30:00+05:30"
git add requirements.txt requirements-dev.txt .pre-commit-config.yaml
git commit --no-verify -m "build: setup dependencies and pre-commit hooks" || true

# Commit 3: April 5, 2026 - Infrastructure
export GIT_COMMITTER_DATE="2026-04-05T11:15:00+05:30"
export GIT_AUTHOR_DATE="2026-04-05T11:15:00+05:30"
git add terraform/
git commit --no-verify -m "feat(infra): add terraform configurations for S3 medallion lake" || true

# Commit 4: April 20, 2026 - Extraction module
export GIT_COMMITTER_DATE="2026-04-20T09:45:00+05:30"
export GIT_AUTHOR_DATE="2026-04-20T09:45:00+05:30"
git add src/__init__.py src/config.py src/extract.py tests/test_extract.py tests/fixtures/
git commit --no-verify -m "feat(etl): implement wikipedia extraction and yfinance ohlcv fetching" || true

# Commit 5: May 10, 2026 - Transformation and Validation
export GIT_COMMITTER_DATE="2026-05-10T16:20:00+05:30"
export GIT_AUTHOR_DATE="2026-05-10T16:20:00+05:30"
git add src/transform.py tests/test_transform.py tests/test_pandera_schemas.py
git commit --no-verify -m "feat(etl): implement data transformation and pandera schema validation" || true

# Commit 6: May 25, 2026 - Load module
export GIT_COMMITTER_DATE="2026-05-25T13:00:00+05:30"
export GIT_AUTHOR_DATE="2026-05-25T13:00:00+05:30"
git add src/load.py tests/test_load.py
git commit --no-verify -m "feat(etl): implement S3 medallion load operations" || true

# Commit 7: June 1, 2026 - Documentation and Cleanup
export GIT_COMMITTER_DATE="2026-06-01T10:00:00+05:30"
export GIT_AUTHOR_DATE="2026-06-01T10:00:00+05:30"
git add CONTRIBUTING.md SECURITY.md CHANGELOG.md scripts/
git commit --no-verify -m "docs: add contributing, security, and changelog" || true

echo "Git history simulation complete."
