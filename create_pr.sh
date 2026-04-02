#!/bin/bash
set -e

echo "Creating feature branch..."
git checkout -b feature/test-ci-demo

echo "Current branch:"
git branch --show-current

echo "Adding comment to routes.py..."
# Comment already added in previous edit

echo "Committing changes..."
git add backend/routes.py
git commit -m "docs(routes): add comment for APIRouter initialization

- Add explanatory comment above router initialization
- Improves code documentation and readability

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "Pushing to remote..."
git push -u origin feature/test-ci-demo

echo "Creating pull request..."
gh pr create --title "docs: add APIRouter initialization comment" --body "## Summary
- Added explanatory comment for APIRouter initialization in routes.py
- Minor documentation improvement to enhance code readability

## Test plan
- [x] Code passes Black formatting check
- [x] No functional changes - documentation only
- [x] Pre-commit hook validation passed

🤖 Generated with [Claude Code](https://claude.com/claude-code)"

echo "Done!"
