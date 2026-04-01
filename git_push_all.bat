@echo off
cls
echo ============================================
echo   Claude Code - Git Auto Push Script
echo ============================================
echo.
echo This script will:
echo   1. Show current git status
echo   2. Stage all changes
echo   3. Create a commit
echo   4. Push to GitHub
echo.
echo ============================================
echo.

echo [Step 1/5] Checking current status...
echo.
git status
echo.

echo ============================================
echo [Step 2/5] Staging all changes...
git add -A
echo.
echo Changes staged successfully!
echo.

echo ============================================
echo [Step 3/5] Files to be committed:
git diff --cached --name-status
echo.

set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=chore: update files via Claude Code

echo.
echo ============================================
echo [Step 4/5] Creating commit with message: %commit_msg%
git commit -m "%commit_msg%"
echo.

echo ============================================
echo [Step 5/5] Pushing to GitHub (origin main)...
git push origin main
echo.

if %errorlevel% equ 0 (
    echo ============================================
    echo SUCCESS! Changes pushed to GitHub
    echo ============================================
    echo.
    echo Recent commits:
    git log --oneline -3
    echo.
    echo View on GitHub:
    git remote get-url origin
) else (
    echo ============================================
    echo ERROR! Push failed
    echo ============================================
    echo Check your internet connection and authentication
)

echo.
echo ============================================
pause
