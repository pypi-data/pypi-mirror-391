# PyPI Packaging Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Prepare pln-search for PyPI publication with proper licensing, metadata, GitHub integration, and CI/CD automation.

**Architecture:** Add MIT license, enhance pyproject.toml with PyPI metadata, extend Makefile with publishing targets, create GitHub Actions workflows for testing and publishing, establish GitHub repository with gh CLI.

**Tech Stack:** Python 3.10+, uv/pip, twine, GitHub Actions, gh CLI, PyPI trusted publishing

---

## Task 1: Create MIT License File

**Files:**
- Create: `LICENSE`

**Step 1: Create LICENSE file with MIT license**

Create file with exact content:

```bash
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 Danny O'Brien

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

**Step 2: Verify LICENSE file created**

Run: `cat LICENSE | head -3`
Expected: Shows "MIT License" and "Copyright (c) 2025 Danny O'Brien"

**Step 3: Commit LICENSE**

```bash
git add LICENSE
git commit -m "chore: add MIT license"
```

---

## Task 2: Update pyproject.toml with PyPI Metadata

**Files:**
- Modify: `pyproject.toml`

**Step 1: Add license, keywords, and classifiers to pyproject.toml**

After the `authors` line (line 8), add:

```toml
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
    "Topic :: Internet",
]
```

**Step 2: Update readme field to use markdown content type**

Replace line 5 `readme = "README.md"` with:

```toml
readme = {file = "README.md", content-type = "text/markdown"}
```

**Step 3: Add project URLs section**

After the classifiers array, add:

```toml

[project.urls]
Homepage = "https://github.com/dannyob/pln-search"
Repository = "https://github.com/dannyob/pln-search"
Issues = "https://github.com/dannyob/pln-search/issues"
```

**Step 4: Verify pyproject.toml syntax**

Run: `uv pip install -e .`
Expected: Successfully reinstalls package without errors

**Step 5: Commit metadata updates**

```bash
git add pyproject.toml
git commit -m "chore: add PyPI metadata to pyproject.toml"
```

---

## Task 3: Add PyPI Publishing Targets to Makefile

**Files:**
- Modify: `Makefile`

**Step 1: Add check-version target**

After the `build:` target (around line 46), add:

```makefile

check-version: ## Check if version needs to be updated for PyPI
	@echo "Current version in pyproject.toml:"
	@grep "^version" pyproject.toml
	@echo ""
	@echo "Latest version on PyPI (if package exists):"
	@python -m pip index versions $(PACKAGE_NAME) 2>/dev/null || echo "Package not found on PyPI (this is normal for new packages)"
```

**Step 2: Add upload-test target**

After check-version, add:

```makefile

upload-test: build ## Upload to TestPyPI
	$(UV) pip install twine
	$(UV) run twine check dist/*
	$(UV) run twine upload --repository testpypi dist/*
	@echo ""
	@echo "Test installation with:"
	@echo "pip install --index-url https://test.pypi.org/simple/ $(PACKAGE_NAME)"
```

**Step 3: Add upload target**

After upload-test, add:

```makefile

upload: build ## Upload to PyPI (production)
	$(UV) pip install twine
	$(UV) run twine check dist/*
	@echo "About to upload to PyPI. This cannot be undone!"
	@read -p "Are you sure? Type 'yes' to continue: " confirm && [ "$$confirm" = "yes" ]
	$(UV) run twine upload dist/*
```

**Step 4: Verify Makefile syntax**

Run: `make help | grep -E "(check-version|upload)"
Expected: Shows all three new targets with descriptions

**Step 5: Test check-version target**

Run: `make check-version`
Expected: Shows current version 0.1.1, says "Package not found on PyPI"

**Step 6: Commit Makefile updates**

```bash
git add Makefile
git commit -m "feat: add PyPI publishing targets to Makefile"
```

---

## Task 4: Create GitHub Actions Test Workflow

**Files:**
- Create: `.github/workflows/test.yml`

**Step 1: Create .github/workflows directory**

```bash
mkdir -p .github/workflows
```

**Step 2: Create test.yml workflow**

```bash
cat > .github/workflows/test.yml << 'EOF'
name: Test

on: [push, pull_request]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
        cache: pip
        cache-dependency-path: pyproject.toml
    - name: Install dependencies
      run: |
        pip install -e .
        pip install pytest pytest-mock requests-mock
    - name: Run tests
      run: |
        python -m pytest -v
EOF
```

**Step 3: Verify YAML syntax**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/test.yml'))"`
Expected: No output (valid YAML)
Note: If pyyaml not installed, skip this check - GitHub will validate

**Step 4: Commit test workflow**

```bash
git add .github/workflows/test.yml
git commit -m "ci: add GitHub Actions test workflow"
```

---

## Task 5: Create GitHub Actions Publish Workflow

**Files:**
- Create: `.github/workflows/publish.yml`

**Step 1: Create publish.yml workflow**

```bash
cat > .github/workflows/publish.yml << 'EOF'
name: Publish Python Package

on:
  release:
    types: [created]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
        cache: pip
        cache-dependency-path: pyproject.toml
    - name: Install dependencies
      run: |
        pip install -e .
        pip install pytest pytest-mock requests-mock
    - name: Run tests
      run: |
        python -m pytest -v

  deploy:
    runs-on: ubuntu-latest
    needs: [test]
    environment: release
    permissions:
      id-token: write
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.13"
        cache: pip
        cache-dependency-path: pyproject.toml
    - name: Install dependencies
      run: |
        pip install build
    - name: Build
      run: |
        python -m build
    - name: Publish
      uses: pypa/gh-action-pypi-publish@release/v1
EOF
```

**Step 2: Verify YAML syntax**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/publish.yml'))"`
Expected: No output (valid YAML)
Note: If pyyaml not installed, skip this check

**Step 3: Commit publish workflow**

```bash
git add .github/workflows/publish.yml
git commit -m "ci: add GitHub Actions publish workflow"
```

---

## Task 6: Test Local Build Process

**Files:**
- None (testing only)

**Step 1: Clean any existing builds**

Run: `make clean`
Expected: Removes build/, dist/, *.egg-info/

**Step 2: Build distribution packages**

Run: `make build`
Expected: Creates dist/pln_search-0.1.1.tar.gz and dist/pln_search-0.1.1-py3-none-any.whl

**Step 3: Verify build contents**

Run: `ls -lh dist/`
Expected: Shows two files (wheel and tarball), both >10KB

**Step 4: Check package with twine**

Run: `uv pip install twine && uv run twine check dist/*`
Expected: "PASSED" for both files, no warnings

Note: No commit - this is verification only

---

## Task 7: Create GitHub Repository

**Files:**
- None (GitHub setup)

**Step 1: Verify gh CLI is authenticated**

Run: `gh auth status`
Expected: Shows "Logged in to github.com as dannyob"
If not logged in: Run `gh auth login` and follow prompts

**Step 2: Create GitHub repository**

Run:
```bash
gh repo create dannyob/pln-search \
  --public \
  --source=. \
  --remote=origin \
  --description="CLI tool for searching the PLN directory API"
```

Expected: Repository created, origin remote added

**Step 3: Verify remote added**

Run: `git remote -v`
Expected: Shows origin pointing to github.com/dannyob/pln-search

**Step 4: Push code to GitHub**

Run: `git push -u origin pypi-packaging`
Expected: Branch pushed, tracking set up

Note: We're on the pypi-packaging branch, so push that first

---

## Task 8: Update README with PyPI Installation

**Files:**
- Modify: `README.md`

**Step 1: Add PyPI installation section**

Replace lines 5-9 (the Installation section) with:

```markdown
## Installation

### From PyPI (recommended)

```bash
pip install pln-search
```

### From source

```bash
git clone https://github.com/dannyob/pln-search.git
cd pln-search
pip install -e .
```
```

**Step 2: Add GitHub badge**

After the first line (`# pln-search`), add:

```markdown

[![Tests](https://github.com/dannyob/pln-search/workflows/Test/badge.svg)](https://github.com/dannyob/pln-search/actions)
```

**Step 3: Verify README renders correctly**

Run: `head -10 README.md`
Expected: Shows title, badge, and installation section

**Step 4: Commit README updates**

```bash
git add README.md
git commit -m "docs: update README with PyPI installation and badge"
```

---

## Task 9: Final Testing and Documentation

**Files:**
- None (verification)

**Step 1: Run full test suite**

Run: `make test`
Expected: All 31 tests pass

**Step 2: Check version is correct**

Run: `make check-version`
Expected: Shows version 0.1.1

**Step 3: Verify all files committed**

Run: `git status`
Expected: "nothing to commit, working tree clean"

**Step 4: Push final changes**

Run: `git push`
Expected: All commits pushed to GitHub

**Step 5: View on GitHub**

Run: `gh repo view --web`
Expected: Opens browser to github.com/dannyob/pln-search

---

## Post-Implementation: Publishing Workflow

**This is documentation, not implementation tasks.**

### For TestPyPI (recommended first):

1. Get TestPyPI token:
   - Visit https://test.pypi.org/manage/account/token/
   - Create token named "pln-search"
   - Save token securely

2. Upload to TestPyPI:
   ```bash
   make upload-test
   # Enter TestPyPI token when prompted
   ```

3. Test installation:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ pln-search
   pln-search --help
   ```

### For Production PyPI:

**Manual Method (first time):**
1. Get PyPI token from https://pypi.org/manage/account/token/
2. `make upload` (enter token when prompted)

**Automated Method (after initial setup):**
1. Configure PyPI Trusted Publishing:
   - Visit https://pypi.org/manage/account/publishing/
   - Add publisher: dannyob/pln-search, workflow: publish.yml
2. Create GitHub Release:
   ```bash
   gh release create v0.1.1 --title "v0.1.1" --notes "Initial PyPI release"
   ```
3. GitHub Actions automatically publishes to PyPI

---

## Success Criteria

- [ ] LICENSE file exists with MIT license
- [ ] pyproject.toml has complete PyPI metadata
- [ ] Makefile has check-version, upload-test, upload targets
- [ ] GitHub Actions workflows created (.github/workflows/test.yml, publish.yml)
- [ ] GitHub repository exists at github.com/dannyob/pln-search
- [ ] README updated with PyPI installation instructions and badge
- [ ] `make build` creates valid packages
- [ ] `make test` passes all 31 tests
- [ ] All changes committed and pushed to GitHub
- [ ] Ready for PyPI publication (manual or via GitHub release)
