@echo off
echo === Staging all changes ===
git add -A

echo.
echo === Git Status ===
git status

echo.
echo === Committing changes ===
git commit -m "feat: add comprehensive documentation, status field, and history endpoint

This commit includes multiple features and documentation updates:

1. CLAUDE.md - Comprehensive coding standards and rules
2. Enhanced README.md with full API documentation
3. docs/API.md - Complete API reference documentation
4. Task status field (todo, in_progress, done, blocked)
5. Task history endpoint GET /tasks/{id}/history
6. Comprehensive test suites for all new features

Changes:
- backend/models.py: Add status field with docstrings
- backend/schemas.py: Add status validation and history schemas
- backend/routes.py: Add history endpoint and status filtering
- backend/crud.py: Add history function and status filtering
- backend/database.py: Enhanced docstrings
- tests/test_status_feature.py: 26 test cases for status
- tests/test_task_history.py: 11 test cases for history
- tests/conftest.py: Enhanced fixture documentation
- tests/test_api.py: Enhanced docstrings
- tests/test_enhanced_api.py: Enhanced docstrings
- tests/test_refactored_api.py: Enhanced docstrings
- alembic/versions/003_add_status_field.py: Migration for status
- CLAUDE.md: 45+ pages of coding standards
- README.md: Comprehensive project documentation
- docs/API.md: Complete API documentation

All changes follow CLAUDE.md rules and best practices.

Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

echo.
echo === Pushing to GitHub ===
git push origin main

echo.
echo === Recent commits ===
git log --oneline -5

echo.
echo === Complete! ===
pause
