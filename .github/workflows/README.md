# GitHub Actions CI/CD with Claude Code

This directory contains GitHub Actions workflows that demonstrate running Claude Code in headless CI mode.

## Workflows

### `claude-code-ci.yml`

Main CI workflow that runs on every push to `main`, pull requests, and can be triggered manually.

**Jobs:**

1. **test-with-claude-code** - Runs tests and code quality checks using Claude Code
   - Sets up Python environment
   - Installs dependencies
   - Runs database migrations
   - Executes linting with Claude Code
   - Runs pytest with coverage
   - Uploads coverage reports

2. **code-review** - AI-powered code review for pull requests
   - Analyzes code changes in PRs
   - Provides feedback on code quality
   - Checks adherence to project guidelines (CLAUDE.md)
   - Posts comments on PRs

3. **documentation-check** - Verifies documentation is up to date
   - Checks API docs match actual endpoints
   - Verifies docstrings are present
   - Ensures documentation follows standards

4. **ci-summary** - Aggregates results from all jobs
   - Provides overall CI status
   - Fails if required checks don't pass

## Setup Instructions

### 1. Add GitHub Secrets

You need to add the following secrets to your GitHub repository:

**Go to:** Repository Settings → Secrets and variables → Actions → New repository secret

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key for Claude | Get from [Anthropic Console](https://console.anthropic.com/) |

**Steps:**
1. Go to https://console.anthropic.com/settings/keys
2. Create a new API key
3. Copy the key
4. Add it to GitHub secrets as `ANTHROPIC_API_KEY`

### 2. Enable GitHub Actions

1. Go to your repository on GitHub
2. Click on **Settings** → **Actions** → **General**
3. Under "Actions permissions", select **Allow all actions and reusable workflows**
4. Under "Workflow permissions", select **Read and write permissions**
5. Click **Save**

### 3. Test the Workflow

**Option A: Push to main branch**
```bash
git add .
git commit -m "feat: add GitHub Actions CI workflow"
git push origin main
```

**Option B: Create a pull request**
```bash
git checkout -b feature/test-ci
git add .
git commit -m "test: verify CI workflow"
git push origin feature/test-ci
# Then create PR on GitHub
```

**Option C: Manual trigger**
1. Go to **Actions** tab in your repository
2. Select **Claude Code CI** workflow
3. Click **Run workflow**
4. Select branch and click **Run workflow**

## Workflow Features

### Headless CI Mode

Claude Code runs in headless mode using the `--headless` flag:

```yaml
claude --headless "Run pytest with coverage report: pytest --cov=backend tests/"
```

This allows Claude Code to:
- Execute commands autonomously
- Parse output and provide analysis
- Generate reports
- Work without user interaction

### Parallel Jobs

The workflow runs multiple jobs in parallel for faster CI:
- Tests run independently from code review
- Documentation checks run in parallel
- Results are aggregated in summary job

### Intelligent Fallbacks

If Claude Code encounters issues, the workflow has fallbacks:

```yaml
- name: Run tests directly (fallback)
  if: failure()
  run: pytest --cov=backend tests/
```

### Artifact Collection

The workflow collects and uploads:
- Test coverage reports
- HTML test reports
- Code review feedback

## Customization

### Adjust Triggers

To run on different branches:

```yaml
on:
  push:
    branches:
      - main
      - develop    # Add more branches
      - 'release/*'
```

### Add More Jobs

Example: Add a deployment job:

```yaml
deploy:
  name: Deploy to Staging
  runs-on: ubuntu-latest
  needs: test-with-claude-code
  if: github.ref == 'refs/heads/main'
  steps:
    - name: Deploy
      run: |
        # Your deployment commands
```

### Customize Claude Code Commands

You can customize what Claude Code does:

```yaml
- name: Custom analysis
  run: |
    claude --headless "Analyze the code for security vulnerabilities and generate a report"
```

## Cost Considerations

**Important:** Claude Code uses the Anthropic API, which incurs costs based on usage.

**To minimize costs:**

1. **Use `continue-on-error: true`** for non-critical checks:
   ```yaml
   - name: Optional check
     continue-on-error: true
     run: claude --headless "..."
   ```

2. **Limit Claude Code usage** to specific scenarios:
   - Only run on pull requests, not every push
   - Use for code review, not simple test execution

3. **Set API usage limits** in Anthropic Console:
   - Configure monthly spending limits
   - Set up usage alerts

4. **Use conditional execution**:
   ```yaml
   if: github.event_name == 'pull_request'  # Only on PRs
   ```

## Monitoring

### View Workflow Runs

1. Go to **Actions** tab in your repository
2. Click on a workflow run to see details
3. Click on individual jobs to see logs

### Check Coverage Reports

Coverage reports are uploaded to Codecov (if configured):
- Badge shows coverage percentage
- Detailed reports show line-by-line coverage

### Review AI Feedback

AI code review comments appear:
- In workflow logs
- As PR comments (if configured)

## Troubleshooting

### Workflow fails with "ANTHROPIC_API_KEY not found"

**Solution:** Add the API key to GitHub secrets (see Setup Instructions above)

### Claude Code CLI not found

**Solution:** The workflow installs it automatically. If it fails, check:
- npm is available (it should be on ubuntu-latest)
- Network connectivity is working

### Tests pass locally but fail in CI

**Solution:** Check environment differences:
- Database configuration (CI uses SQLite by default)
- Environment variables
- Python version (CI uses 3.11)

### Workflow is too slow

**Solution:** Optimize by:
- Running fewer Claude Code analyses
- Using `continue-on-error: true` for non-critical checks
- Caching dependencies (already enabled for pip)

## Best Practices

1. **Don't overuse Claude Code** - Use it for tasks that benefit from AI analysis (code review, documentation checks), not simple test execution

2. **Monitor API usage** - Keep track of costs in Anthropic Console

3. **Use caching** - The workflow caches pip dependencies to speed up runs

4. **Test locally first** - Before pushing, test your changes:
   ```bash
   pytest --cov=backend tests/
   flake8 backend/
   ```

5. **Review logs** - Always check workflow logs to understand failures

## Example: Running Locally

You can run similar commands locally:

```bash
# Install Claude Code CLI
npm install -g @anthropic/claude-code

# Set API key
export ANTHROPIC_API_KEY=your-api-key

# Run in headless mode
claude --headless "Run pytest with coverage: pytest --cov=backend tests/"
```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Claude Code Documentation](https://code.claude.com/)
- [Anthropic API Documentation](https://docs.anthropic.com/)

## Support

If you encounter issues:
1. Check workflow logs in GitHub Actions
2. Review this documentation
3. Check project's CLAUDE.md for coding standards
4. Consult GitHub Actions and Claude Code documentation
