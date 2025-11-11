# Version Management Guide

## Overview

This project uses **semantic-release** to automatically manage versions based on [Conventional Commits](https://www.conventionalcommits.org/). 

**Key principles:**
- **Production versions**: Let semantic-release handle them automatically
- **TestPyPI versions**: Use `-rc` (release candidate) suffixes (e.g., `1.0.9-rc.1`)
- **Local testing**: Don't bump version, just test with current version

## How It Works

1. **Commit with conventional format** (e.g., `feat:`, `fix:`, `BREAKING:`)
2. **Push to main branch**
3. **CI runs semantic-release** which:
   - Analyzes commit messages
   - Determines version bump (major/minor/patch)
   - Updates `package.json` version
   - Creates git tag (e.g., `v1.0.12`)
   - Pushes tag to GitHub
4. **Python version syncs automatically** via `hatch-nodejs-version` from `package.json`

## Commit Message Format

| Commit Type | Version Bump | Example |
|------------|--------------|---------|
| `feat: ...` | **Minor** (1.0.11 → 1.1.0) | `feat: add new model browser` |
| `fix: ...` | **Patch** (1.0.11 → 1.0.12) | `fix: resolve CORS issue` |
| `BREAKING: ...` | **Major** (1.0.11 → 2.0.0) | `BREAKING: change API interface` |
| No prefix | **None** | `docs: update README` |

## ❌ What NOT to Do

**NEVER manually edit the version in `package.json`** when using semantic-release. This causes mismatches:

```bash
# ❌ BAD - Don't do this!
# Manually editing package.json version
# This will cause semantic-release to create a different tag
```

## ✅ Correct Workflow

### For Regular Releases

1. **Make your changes**
2. **Commit with conventional format:**
   ```bash
   git commit -m "fix: remove server extension dependency"
   git push origin main
   ```
3. **Wait for CI to complete:**
   - Tests run
   - semantic-release analyzes commits
   - Version bumped in `package.json` (if needed)
   - Git tag created and pushed
4. **Publish to TestPyPI/PyPI:**
   - Use the version that semantic-release created
   - Or wait for the publish workflow to run automatically

### For Local Testing

**You don't need to bump the version for local testing!** Just test with the current version:

```bash
# Make your changes
vim src/api/client.ts

# Build and test locally (version doesn't matter for local testing)
python3 -m build
# Test the built package

# Commit your changes (without any version bump)
git add src/api/client.ts
git commit -m "fix: call BioLM API directly from client"
git push origin main
# semantic-release will handle the version bump
```

### For TestPyPI Publishing (Recommended: Use -rc suffixes)

**Best Practice: Always use `-rc` (release candidate) suffixes for TestPyPI**

This ensures TestPyPI versions don't conflict with semantic-release's production versions:

```bash
# 1. Make your changes and commit
git commit -m "fix: some bug fix"

# 2. Bump to release candidate version
npm version 1.0.9-rc.1 --no-git-tag-version
git add package.json
git commit -m "chore: bump to 1.0.9-rc.1 for TestPyPI"

# 3. Build and publish to TestPyPI
python3 -m build
python3 -m twine upload --repository testpypi dist/jupyterlab_biolm-1.0.9-rc.1*

# 4. Push commits (semantic-release will create 1.0.9 when ready)
git push origin main
# When semantic-release runs, it will create v1.0.9 (which is > 1.0.9-rc.1)
```

**Why `-rc` suffixes?**
- ✅ TestPyPI versions are clearly marked as pre-release
- ✅ semantic-release can still create the final version (1.0.9 > 1.0.9-rc.1)
- ✅ No version conflicts
- ✅ Standard practice in the industry

**Alternative: Wait for semantic-release**
```bash
# Just push your commit and wait
git push origin main
# Wait for CI/semantic-release to create the tag
git fetch --tags
# Use the version from the tag for publishing
```

## Current Version Status

To check the current version:

```bash
# Check package.json
cat package.json | grep '"version"'

# Check latest git tag
git describe --tags --abbrev=0

# Check what semantic-release will do (dry run)
npx semantic-release --dry-run
```

## Troubleshooting Version Mismatches

If you see a mismatch between `package.json` and git tags:

1. **Check what semantic-release created:**
   ```bash
   git fetch --tags
   git tag --sort=-version:refname | head -5
   ```

2. **Align versions:**
   - If `package.json` is ahead: Let semantic-release handle it on the next commit
   - If tags are ahead: Pull the semantic-release commit that updated `package.json`

3. **Reset if needed:**
   ```bash
   # Only if absolutely necessary - this is destructive!
   # Pull the version from the latest tag
   git checkout v1.0.8 -- package.json
   ```

## Best Practices

1. ✅ **Always use conventional commits** (`feat:`, `fix:`, etc.)
2. ✅ **Let semantic-release handle all production version bumps**
3. ✅ **Publish to TestPyPI/PyPI after semantic-release creates the tag**
4. ✅ **Don't bump version for local testing** (just test with current version)
5. ✅ **Use `-rc` suffixes for TestPyPI** (e.g., `1.0.9-rc.1`) - this is the standard practice
6. ❌ **Never manually edit `package.json` version for production releases** (let semantic-release do it)
7. ❌ **Never create git tags manually** (let semantic-release do it)
8. ❌ **Never bump version just to revert it** (that workflow doesn't make sense)

## Example Workflows

### Standard Release Workflow

```bash
# 1. Make changes
vim src/api/client.ts

# 2. Commit with conventional format
git add src/api/client.ts
git commit -m "fix: call BioLM API directly from client"

# 3. Push
git push origin main

# 4. Wait for CI
# - CI runs tests
# - semantic-release creates v1.0.12 tag
# - package.json updated to 1.0.12

# 5. Publish (if needed)
# Use the version from the tag: 1.0.12
python3 -m build
python3 -m twine upload --repository testpypi dist/jupyterlab_biolm-1.0.12*
```

### Local Testing Workflow

```bash
# 1. Make changes
vim src/api/client.ts

# 2. Build and test locally (no version bump needed!)
python3 -m build
# Test the built package locally

# 3. Commit your changes (without any version bump)
git add src/api/client.ts
git commit -m "fix: call BioLM API directly from client"

# 4. Push (semantic-release will create the version)
git push origin main
```

### TestPyPI Publishing Workflow (using -rc suffixes)

```bash
# Recommended workflow for TestPyPI publishing:

# 1. Make your changes and commit
git add src/api/client.ts
git commit -m "fix: call BioLM API directly from client"

# 2. Bump to release candidate version
npm version 1.0.9-rc.1 --no-git-tag-version
git add package.json
git commit -m "chore: bump to 1.0.9-rc.1 for TestPyPI"

# 3. Build and publish to TestPyPI
python3 -m build
python3 -m twine upload --repository testpypi dist/jupyterlab_biolm-1.0.9-rc.1*

# 4. Push commits
git push origin main

# 5. semantic-release will create 1.0.9 when it runs
# (1.0.9 > 1.0.9-rc.1, so no conflict)
```

## Configuration

The semantic-release configuration is in `package.json`:

```json
{
  "release": {
    "branches": ["main", "master"],
    "plugins": [
      "@semantic-release/commit-analyzer",
      "@semantic-release/release-notes-generator",
      ["@semantic-release/npm", { "npmPublish": false }],
      ["@semantic-release/git", {
        "assets": ["package.json"],
        "message": "chore(release): ${nextRelease.version} [skip ci]"
      }]
    ]
  }
}
```

This configuration:
- Analyzes commits for version bumps
- Updates `package.json` with new version
- Creates git tag
- Commits the version bump back to the repo
- Skips CI on the version bump commit (to avoid loops)

