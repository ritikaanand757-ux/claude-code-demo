@echo off
echo ================================
echo Git Status and Push Script
echo ================================

echo.
echo Current Directory:
cd

echo.
echo === Step 1: Checking Git Status ===
git status

echo.
echo === Step 2: Showing Untracked/Modified Files ===
git status --short

echo.
echo === Step 3: Adding All Changes ===
git add -A
echo Files staged successfully!

echo.
echo === Step 4: Showing Staged Files ===
git diff --cached --name-status

echo.
echo === Step 5: Creating Commit ===
git commit -m "feat(ci): add GitHub Actions workflow with Claude Code integration" -m "- Added .github/workflows/claude-code-ci.yml" -m "- Added .github/workflows/README.md" -m "- Updated README.md with CI/CD section"

echo.
echo === Step 6: Showing Recent Commits ===
git log --oneline -3

echo.
echo === Step 7: Checking Remote ===
git remote -v

echo.
echo === Step 8: Pushing to GitHub ===
git push origin main

echo.
echo === Step 9: Verifying Push ===
git log origin/main -1 --oneline

echo.
echo ================================
echo Script Complete!
echo ================================
pause
