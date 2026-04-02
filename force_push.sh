#!/bin/bash
# Force push all changes to GitHub

cd "C:/Users/2000185351/claude-code-demo"

echo "=== Adding all changes ==="
git add backend/auth.py
git add .github/workflows/claude-code-ci.yml
git add Makefile

echo "=== Current status ==="
git status

echo "=== Committing changes ==="
git commit -m "fix(auth): force password truncation to 72 bytes for bcrypt"

echo "=== Pushing to GitHub ==="
git push origin feature/test-ci-demo --force

echo "=== Push complete! ==="
