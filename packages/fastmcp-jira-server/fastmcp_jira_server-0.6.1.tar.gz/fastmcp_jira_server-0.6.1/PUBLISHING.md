# Publishing to PyPI

This document describes how to publish the fastmcp-jira-server package to PyPI.

## Prerequisites

1. **GitHub Repository**: The code must be in a GitHub repository at `troylar/jira-mcp-server`
2. **PyPI Account**: You need a PyPI account at https://pypi.org
3. **Trusted Publishing**: Set up trusted publishing (recommended) or API token

## Publishing Methods

### Method 1: Automatic Publishing via GitHub Releases (Recommended)

This method uses GitHub Actions with trusted publishing (no API tokens needed).

#### Setup Trusted Publishing on PyPI

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new publisher"
3. Fill in:
   - **PyPI Project Name**: `fastmcp-jira-server`
   - **Owner**: `troylar`
   - **Repository name**: `jira-mcp-server`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`
4. Click "Add"

#### Create a Release

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Create a new tag (e.g., `v0.5.0`)
4. Title: `v0.5.0 - Comment Management`
5. Description: Describe the release
6. Click "Publish release"

The GitHub Action will automatically:
- Build the package
- Run all tests
- Publish to PyPI

### Method 2: Manual Publishing via Workflow Dispatch (Test PyPI)

For testing, you can manually trigger the publish workflow:

1. Go to Actions → "Publish to PyPI"
2. Click "Run workflow"
3. Select branch
4. Check "Publish to TestPyPI" for testing
5. Click "Run workflow"

#### Setup Test PyPI Trusted Publishing

1. Go to https://test.pypi.org/manage/account/publishing/
2. Follow the same steps as above, but use environment name: `testpypi`

### Method 3: Manual Local Publishing (Not Recommended)

If you need to publish manually:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the package
twine check dist/*

# Upload to Test PyPI (for testing)
twine upload --repository testpypi dist/*

# Upload to PyPI (production)
twine upload dist/*
```

## Version Management

Update the version in `pyproject.toml` before creating a release:

```toml
[project]
version = "0.5.0"  # Update this
```

Follow semantic versioning:
- **Major** (1.0.0): Breaking changes
- **Minor** (0.5.0): New features, backwards compatible
- **Patch** (0.5.1): Bug fixes

## CI/CD Workflows

### CI Workflow (`.github/workflows/ci.yml`)

Runs on every push and pull request:
- Tests on Python 3.10, 3.11, 3.12, 3.13
- Runs ruff linting and formatting checks
- Runs mypy type checking
- Runs pytest with 100% coverage requirement
- Uploads coverage to Codecov

### Publish Workflow (`.github/workflows/publish.yml`)

Runs on release creation or manual trigger:
- Builds the package
- Runs all tests
- Publishes to PyPI using trusted publishing
- Can publish to TestPyPI for testing

## Verifying the Package

After publishing, verify the package:

```bash
# Install from PyPI
pip install fastmcp-jira-server

# Verify it works
fastmcp-jira-server --help

# Or in Python
python -c "import jira_mcp_server; print(jira_mcp_server.__version__)"
```

## Troubleshooting

### Build Fails

- Check that all dependencies are specified in `pyproject.toml`
- Run `python -m build` locally to test
- Check `twine check dist/*` output

### Tests Fail in CI

- Tests must pass with 100% coverage
- Run `pytest --cov=src/jira_mcp_server --cov-fail-under=100` locally
- Check for environment-specific issues

### Publishing Fails

- **Trusted publishing**: Verify the repository, workflow name, and environment match exactly
- **Manual**: Check API token permissions
- **Version conflict**: Version already exists on PyPI (update version)

### Package Not Found After Publishing

- PyPI indexing can take a few minutes
- Check the package page: https://pypi.org/project/fastmcp-jira-server/
- Clear pip cache: `pip cache purge`

## Security Best Practices

1. **Use Trusted Publishing**: No need to store API tokens
2. **Never commit tokens**: Keep API tokens in GitHub Secrets only
3. **Use TestPyPI first**: Test releases on test.pypi.org before production
4. **Sign releases**: Consider signing releases with GPG

## Package Metadata

The package metadata is defined in `pyproject.toml`:

- **Name**: fastmcp-jira-server
- **Version**: 0.5.0
- **Python**: >=3.10
- **License**: MIT
- **Homepage**: https://github.com/troylar/jira-mcp-server

## Release Checklist

Before creating a release:

- [ ] All tests pass locally
- [ ] Version updated in `pyproject.toml`
- [ ] CHANGELOG updated (if applicable)
- [ ] README updated with new features
- [ ] All commits pushed to main branch
- [ ] CI passing on GitHub
- [ ] Create GitHub release with tag
- [ ] Verify package on PyPI after publish
- [ ] Test installation: `pip install fastmcp-jira-server`

## Support

For issues with publishing:
- GitHub Issues: https://github.com/troylar/jira-mcp-server/issues
- PyPI Help: https://pypi.org/help/
