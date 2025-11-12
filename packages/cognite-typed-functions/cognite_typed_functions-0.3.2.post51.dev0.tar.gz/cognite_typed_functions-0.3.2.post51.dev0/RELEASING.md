# Release Process

This document describes the release process for `cognite-typed-functions` and explains the design decisions behind it.

## Overview

Our release process is designed to:

- Use **git tags** as the single source of truth for versioning
- Leverage **GitHub's UI for creating and maintaining changelogs** for each release
- Avoid **manual version number updates** in PRs (prevents merge conflicts)
- Comply with **GitHub environment protection rules** (CD environment cannot be deployed from tags)
- Provide a **manual review step** before publishing to PyPI

## Why This Process?

### The Problem

We want to avoid the common pitfall where developers manually update version numbers in their PRs. This leads to:

- **Merge conflicts**: Multiple PRs touching version files create conflicts
- **Version coordination overhead**: Developers need to coordinate who updates what version
- **Inconsistent versioning**: Easy to forget to update all version references

### The Solution

We use **git tags** for version management and **GitHub's UI for changelog management**:

**Versioning:**

- Version numbers are **never stored in source code** during development
- `dunamai` automatically derives versions from git tags at build time
- During development, versions are dev versions (e.g., `0.1.0.dev5+g1a2b3c4`)
- For releases, the Python package version is derived from the git tag:
  - Git tag: `v0.1.0` (always with `v` prefix)
  - Package version: `0.1.0` (without `v` prefix)
  - `dunamai` automatically strips the `v` prefix when generating the package version

**Changelog Management:**

- GitHub automatically generates changelogs from merged PRs and commit messages
- All release notes are maintained in the GitHub Releases UI
- This provides a single source of truth for what changed in each version
- Users can view changelogs directly on the repository's Releases page
- No need to maintain a separate `CHANGELOG.md` file that can get out of sync

### GitHub Protection Rules

Our CD environment requires deployments from the `main` branch, not from tags. This security policy prevents direct tag-based deployments, requiring us to:

1. Create a release branch from the tag
2. Review and merge to `main` via PR
3. Publish from `main` branch

This adds a manual step but provides better security and review controls.

## Release Workflow

### Step 1: Create a GitHub Release

When you're ready to release a new version:

1. Go to the [Releases](https://github.com/cognitelabs/cognite-typed-functions/releases) page
2. Click **"Draft a new release"**
3. Click **"Choose a tag"** and create a new tag (e.g., `v0.1.1`)
   - Follow semantic versioning: `v<major>.<minor>.<patch>`
4. Set the release title (e.g., `v0.1.1`)
5. Click **"Generate release notes"** to auto-generate changelog from merged PRs
   - This is a key feature: GitHub automatically creates a changelog from all merged PRs since the last release
   - The generated notes include PR titles, authors, and links
   - This becomes the official changelog for this version
6. Review and edit the release notes as needed
   - You can add additional context, breaking changes, or upgrade instructions
   - You can categorize changes (Features, Bug Fixes, etc.)
7. Click **"Publish release"**

**Note:** The GitHub release UI is the single source of truth for changelogs. Users will look here to see what changed between versions.

### Step 2: Automatic Branch Creation

The `release-pr.yml` workflow will automatically:

- Check out the release tag
- Create a branch named `release/v0.1.1`
- Run `dunamai` to extract the version from the tag
- Update `src/cognite_typed_functions/_version.py` with the version
- Push the branch to GitHub

### Step 3: Create Pull Request Manually

**Important**: You must create the PR manually due to security policies.

1. Go to the repository and you'll see a prompt to create a PR from the new branch
2. Create a PR from `release/v0.1.1` → `main`
3. Title: `Release v0.1.1`
4. Description should include:

   ```markdown
   Release v0.1.1

   Release notes: [link to release]

   Once merged, the package will be automatically published to PyPI.
   ```

### Step 4: Review and Merge

1. Review the PR (mainly the version update)
2. Get required approvals per your security policy
3. Merge the PR into `main`

### Step 5: Automatic Publication

When the PR is merged to `main`, the `python-publish.yml` workflow will automatically:

- Check out `main`
- Use `dunamai` to detect the version from git tags
- Build the package with the correct version
- Publish to PyPI

## Important Notes

### Version Numbers in Development

**Do not manually update version numbers in your PRs!**

During development:

- Version numbers are automatically derived from git tags by `dunamai`
- Development builds use dev versions without the `v` prefix (e.g., `0.1.0.dev5+g1a2b3c4`)
- The version in `_version.py` is automatically generated during build
- Remember: Git tags use `v0.1.0`, but Python package versions use `0.1.0`

### Version File

The `src/cognite_typed_functions/_version.py` file:

- Is **auto-generated** during the release process
- Should **not be manually edited** in development PRs
- Gets updated by the release workflow when a release branch is created

### Semantic Versioning

Follow [semantic versioning](https://semver.org/) guidelines:

- `MAJOR`: Breaking changes
- `MINOR`: New features (backwards compatible)
- `PATCH`: Bug fixes (backwards compatible)

**Important:** Git tags must always use the format `vX.Y.Z` (with lowercase `v` prefix):

- ✅ Correct: `v1.0.0`, `v1.1.0`, `v1.1.1`
- ❌ Incorrect: `1.0.0`, `V1.0.0`, `version-1.0.0`

## Troubleshooting

### Release workflow fails

- Check that you have write permissions to the repository
- Ensure the tag follows the format `vX.Y.Z`

### Publish workflow fails

- Check that the `PYPI_API_TOKEN` secret is set correctly
- Verify that the version doesn't already exist on PyPI
- Ensure the CD environment protection rules are satisfied

### Version conflicts

If you accidentally have version updates in your PR:

- Remove the changes to `_version.py`
- The correct version will be set during the release process

## Summary

This process may seem manual, but it provides:

- ✅ **No merge conflicts** on version numbers
- ✅ **GitHub-managed changelogs** - single source of truth for release notes
- ✅ **Manual review** before publishing
- ✅ **Compliance** with security policies
- ✅ **Automatic versioning** from git tags
- ✅ **Clean git history** without version update commits

The extra manual PR creation step is required by our security policy and ensures proper review before publishing to PyPI. The use of GitHub's release UI means we never have to maintain separate changelog files or worry about them getting out of sync.
