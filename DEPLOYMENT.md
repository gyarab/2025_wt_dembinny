# Deployment Workflow Guide

This repository uses a multi-environment deployment strategy for GitHub Pages:

## Environments

### 1. Production Environment
- **Branch**: `main`
- **Workflow**: `.github/workflows/static.yml`
- **URL**: Main GitHub Pages URL (root)
- **Purpose**: Live production site
- **Deployment**: To `gh-pages` branch (root directory)

### 2. Staging Environment
- **Branch**: `staging`
- **Workflow**: `.github/workflows/deploy-staging.yml`
- **Purpose**: Preview and test changes before going to production
- **Visual Indicator**: Orange warning banner at the top of every page
- **Deployment**: To `gh-pages` branch (root directory, replaces production temporarily)
- **Note**: Deployments to staging will temporarily replace the production site. To restore production, redeploy from main.

### 3. PR Preview Environment (NEW!)
- **Trigger**: Pull Requests
- **Workflow**: `.github/workflows/deploy-pr-preview.yml`
- **URL**: `https://[owner].github.io/[repo]/pr-preview/pr-[number]/`
- **Purpose**: Automatic preview for each pull request
- **Visual Indicator**: Purple "PR Preview" banner at the top of every page
- **Deployment**: To `gh-pages` branch in `pr-preview/pr-[number]/` subdirectory
- **Benefits**:
  - Each PR gets its own unique preview URL
  - Multiple PRs can have previews simultaneously
  - Automatic comment on PR with preview link and QR code
  - Automatic cleanup when PR is closed
  - Does NOT interfere with production or other PRs

## How to Use

### Working with Pull Request Previews (Recommended for Collaboration)

1. **Create a feature branch and make changes:**
   ```bash
   git checkout -b feature/my-feature
   # Edit your files
   git add .
   git commit -m "Add new feature"
   git push origin feature/my-feature
   ```

2. **Create a Pull Request on GitHub:**
   - Go to the repository on GitHub
   - Click "Pull Requests" → "New Pull Request"
   - Select your feature branch
   - Create the pull request

3. **Automatic Preview Deployment:**
   - The PR Preview workflow automatically runs
   - A comment is posted on your PR with:
     - Direct link to the preview
     - QR code for mobile testing
   - Preview URL: `https://gyarab.github.io/2025_wt_dembinny/pr-preview/pr-[NUMBER]/`

4. **Update the Preview:**
   - Make more commits to your feature branch
   - Push to GitHub
   - The preview automatically updates
   - The PR comment updates with the new deployment info

5. **Test and Review:**
   - Share the preview URL with team members
   - Test on different devices (use QR code for mobile)
   - Get feedback directly on the PR

6. **Merge to Production:**
   - When the PR is approved and merged to `main`
   - Production automatically deploys
   - The PR preview is automatically cleaned up

### Testing Changes on Staging

1. **Create or checkout the staging branch:**
   ```bash
   git checkout -b staging
   # or if it already exists:
   git checkout staging
   ```

2. **Make your changes:**
   ```bash
   # Edit your files
   git add .
   git commit -m "Your changes"
   ```

3. **Push to staging:**
   ```bash
   git push origin staging
   ```

4. **Wait for deployment:**
   - Go to the "Actions" tab on GitHub
   - Wait for the "Deploy staging to Pages" workflow to complete
   - Click on the workflow run to see the deployment URL

5. **Preview your changes:**
   - Visit your GitHub Pages URL (same as production)
   - You'll see an orange warning banner indicating it's staging
   - The staging deployment temporarily replaces production
   - Test all your changes

6. **If everything looks good, merge to main:**
   ```bash
   git checkout main
   git merge staging
   git push origin main
   ```
   - This will redeploy to production (without the warning banner)
   - Production is restored

### Direct Production Deployment

If you're confident in your changes and don't need staging:

```bash
git checkout main
# Make changes
git add .
git commit -m "Your changes"
git push origin main
```

## Workflow Files

### Production Workflow (`static.yml`)
- Triggered by pushes to `main` branch
- Deploys to `gh-pages` branch (root directory)
- No visual indicators (clean production site)
- Preserves `pr-preview/` directory (doesn't delete PR previews)

### Staging Workflow (`deploy-staging.yml`)
- Triggered by pushes to `staging` branch
- Deploys to `gh-pages` branch (root directory)
- Adds orange warning banner to indicate staging
- Can be cancelled if newer push comes in
- Temporarily replaces production

### PR Preview Workflow (`deploy-pr-preview.yml`) - NEW!
- Triggered by pull request events (opened, updated, closed)
- Deploys to `gh-pages` branch in `pr-preview/pr-[number]/` subdirectory
- Adds purple "PR Preview" banner to indicate PR preview
- Posts automatic comment on PR with preview link and QR code
- Automatically cleans up when PR is closed
- Multiple PR previews can coexist simultaneously

## Benefits

✅ **PR Previews**: Each pull request gets its own automatic preview URL
✅ **No conflicts**: Multiple PRs can have previews at the same time
✅ **Easy collaboration**: Share preview links with team members for review
✅ **Mobile testing**: QR codes in PR comments for quick mobile access
✅ **Automatic cleanup**: Previews removed when PRs are closed
✅ **No spam commits to main**: Test on PR previews or staging first
✅ **Safe experimentation**: Break things on PR previews, not production
✅ **Visual distinction**: Different colored banners for production/staging/PR previews
✅ **Easy rollback**: Keep main branch stable, redeploy to restore production
✅ **Workflow testing**: Test the entire build and deployment process before production
✅ **Build validation**: Ensure no errors before merging to main

**Note**: With PR previews, each pull request gets its own subdirectory, so multiple PRs can have previews simultaneously without conflicts. However, staging and production still share the root URL, so staging temporarily replaces production.

## GitHub Pages Configuration

**IMPORTANT**: To use PR previews, you must configure GitHub Pages to deploy from a branch:

### Required Setup Steps

1. **Go to Settings → Pages**
2. **Set Source to "Deploy from a branch"**:
   - Under "Build and deployment"
   - Source: **Deploy from a branch** (NOT "GitHub Actions")
   - Branch: Select `gh-pages` and `/ (root)`
   - Click Save

3. **Enable workflow permissions**:
   - Go to Settings → Actions → General
   - Under "Workflow permissions"
   - Select "Read and write permissions"
   - Check "Allow GitHub Actions to create and approve pull requests"
   - Click Save

### Why These Settings?

- **Branch deployment**: PR preview action requires deploying to a branch (`gh-pages`)
- **Write permissions**: Workflows need to push to the `gh-pages` branch
- The `gh-pages` branch will be automatically created on first deployment

### Deployment Structure on gh-pages Branch

```
gh-pages branch:
├── index.html                    (Production from main)
├── microsite/                    (Production files)
├── prvni-web/                    (Production files)
├── file_giver/                   (Production files)
└── pr-preview/                   (PR previews directory)
    ├── pr-1/                     (Preview for PR #1)
    │   ├── index.html
    │   └── ...
    ├── pr-2/                     (Preview for PR #2)
    │   ├── index.html
    │   └── ...
    └── ...
```

Each environment deploys to a different location:
- **Production** (`main` branch) → `gh-pages` root
- **Staging** (`staging` branch) → `gh-pages` root (replaces production temporarily)
- **PR Previews** → `gh-pages/pr-preview/pr-[number]/` (unique per PR)

## Troubleshooting

**Q: I pushed to staging but nothing happened**
- Check the Actions tab for workflow runs
- Ensure the workflow file exists at `.github/workflows/deploy-staging.yml`
- Check if there are any errors in the workflow run

**Q: PR preview deployment failed**
- Ensure GitHub Pages is set to "Deploy from a branch" (not "GitHub Actions")
- Check that workflow permissions are set to "Read and write"
- Verify the `gh-pages` branch exists (it's created automatically on first deploy)
- Look at the Actions tab for error messages

**Q: Can I view staging and production at the same time?**
- No, GitHub Pages (with Actions source) allows only one active deployment
- Staging temporarily replaces production on the same URL
- The orange banner helps you know which version is deployed
- To restore production, push to main or use workflow_dispatch

**Q: Can I have multiple staging branches?**
- The current setup uses one staging branch
- You could create additional workflow files for other branches if needed

**Q: How do I delete staging?**
- Simply delete the staging branch: `git push origin --delete staging`
- The staging environment will remain in GitHub but won't be updated
