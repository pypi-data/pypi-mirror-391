# PyPI Packaging Design for pln-search

**Date:** 2025-11-13
**Status:** Approved for Implementation
**Goal:** Prepare pln-search for PyPI publication with GitHub integration and CI/CD automation

## Overview

Transform the existing pln-search CLI tool into a PyPI-ready package following the patterns established in llm-tools-todo. This includes adding proper licensing, comprehensive metadata, publishing workflows, and automated testing/deployment via GitHub Actions.

## Requirements

### Must Have
- MIT license file
- Complete PyPI metadata (repository URLs, keywords, classifiers)
- Makefile targets for PyPI publishing (upload, upload-test, check-version)
- GitHub repository at https://github.com/dannyob/pln-search
- GitHub Actions for automated testing on push/PR
- GitHub Actions for automated PyPI publishing on release
- README.md used as PyPI long description

### Nice to Have
- Test coverage badge in README
- Automated version checking

### Explicitly Out of Scope
- CHANGELOG.md (add later when more versions exist)
- Documentation site (README sufficient for now)

## Design

### 1. Licensing

**File:** `LICENSE`
**Content:** MIT License with Danny O'Brien as copyright holder
**Rationale:** MIT is most permissive, allows commercial use, most popular for Python packages

### 2. PyPI Metadata

**File:** `pyproject.toml` additions

```toml
[project]
# ... existing fields ...
license = {text = "MIT"}
keywords = ["pln", "directory", "search", "cli", "protocol-labs", "filecoin"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Utilities",
]

[project.urls]
Homepage = "https://github.com/dannyob/pln-search"
Repository = "https://github.com/dannyob/pln-search"
Issues = "https://github.com/dannyob/pln-search/issues"

[project]
# Use README.md as PyPI description
readme = {file = "README.md", content-type = "text/markdown"}
```

**Rationale:**
- Keywords improve PyPI search discoverability
- Classifiers help users filter by Python version, license, maturity
- URLs provide navigation from PyPI to GitHub
- README.md provides rich formatted documentation on PyPI page

### 3. Makefile Publishing Targets

Add targets matching llm-tools-todo pattern:

**`make check-version`**
- Shows current version from pyproject.toml
- Shows latest PyPI version (or "not found" for new packages)
- Helps avoid publishing with stale version number

**`make upload-test`**
- Builds distribution (calls `make build`)
- Validates with `twine check dist/*`
- Uploads to TestPyPI
- Displays test installation command
- Safe testing before production publish

**`make upload`**
- Builds distribution
- Validates with `twine check dist/*`
- Requires manual confirmation ("Are you sure? Type 'yes'")
- Uploads to production PyPI
- Cannot be undone - confirmation prevents accidents

**Dependencies to add:**
- `build` - Creates wheel and sdist
- `twine` - Secure PyPI upload tool

### 4. GitHub Repository Setup

**Creation:** Use `gh repo create` to establish repository

```bash
gh repo create dannyob/pln-search --public --source=. --remote=origin
```

**Initial push:**
- Push main branch with all current code
- Ensures code is backed up and shareable

**Future workflow:**
- Create releases via GitHub UI or `gh release create`
- Releases trigger automated PyPI publishing

### 5. GitHub Actions - Testing

**File:** `.github/workflows/test.yml`

**Trigger:** Every push and pull request
**Strategy:** Matrix testing across Python 3.10, 3.11, 3.12, 3.13
**Steps:**
1. Checkout code
2. Setup Python with pip caching
3. Install package with test dependencies
4. Run pytest

**Benefits:**
- Catches bugs before they reach production
- Ensures compatibility across Python versions
- Tests run automatically - no manual work
- Visible status badges for README

### 6. GitHub Actions - Publishing

**File:** `.github/workflows/publish.yml`

**Trigger:** GitHub Release creation (e.g., tag `v0.1.2`)
**Jobs:**
1. **test** - Full test matrix (3.10-3.13)
2. **deploy** - Only runs if tests pass
   - Builds package
   - Publishes to PyPI via trusted publishing

**Trusted Publishing Setup:**
- Modern PyPI feature (no API tokens needed)
- GitHub Actions authenticates directly to PyPI
- One-time setup: Add GitHub repo as trusted publisher on PyPI
- More secure than managing API tokens

**Publishing Workflow:**
1. Update version in pyproject.toml
2. Commit and push
3. Create GitHub Release with tag (e.g., `v0.1.2`)
4. GitHub Actions automatically tests and publishes
5. Package appears on PyPI within minutes

## Implementation Plan

### Phase 1: Files and Metadata
1. Create LICENSE file (MIT)
2. Update pyproject.toml with complete metadata
3. Update Makefile with publishing targets
4. Test build locally (`make build`)

### Phase 2: GitHub Setup
1. Create GitHub repo with `gh repo create`
2. Push code to GitHub
3. Verify repository appears correctly

### Phase 3: CI/CD Setup
1. Create `.github/workflows/test.yml`
2. Create `.github/workflows/publish.yml`
3. Push workflows to GitHub
4. Verify test workflow runs on push

### Phase 4: PyPI Trusted Publishing
1. Visit PyPI.org (or TestPyPI for testing)
2. Add dannyob/pln-search as trusted publisher
3. Test with GitHub release on TestPyPI first
4. Verify automated publishing works

### Phase 5: Documentation
1. Update README with PyPI installation instructions
2. Add GitHub Actions badge
3. Document release process for future versions

## Success Criteria

- [ ] `make build` creates valid wheel and sdist
- [ ] `make upload-test` successfully uploads to TestPyPI
- [ ] Package installs from TestPyPI: `pip install -i https://test.pypi.org/simple/ pln-search`
- [ ] GitHub Actions test workflow passes on push
- [ ] GitHub repository visible at https://github.com/dannyob/pln-search
- [ ] Ready for production PyPI publish (but not published yet per requirements)

## Future Enhancements

After initial PyPI setup:
- Add CHANGELOG.md for version history
- Add test coverage reporting
- Consider automated version bumping tools
- Add documentation site (mkdocs or sphinx) if needed

## References

- Template project: ~/Public/src/llm-tools-todo
- PyPI Trusted Publishing: https://docs.pypi.org/trusted-publishers/
- GitHub Actions: https://docs.github.com/en/actions
