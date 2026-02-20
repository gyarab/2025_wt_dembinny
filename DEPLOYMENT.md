# Deployment Workflow Guide

This repository uses a two-environment deployment strategy for GitHub Pages:

## Environments

### 1. Production Environment
- **Branch**: `main`
- **Workflow**: `.github/workflows/static.yml`
- **URL**: Main GitHub Pages URL
- **Purpose**: Live production site

### 2. Staging/Preview Environment
- **Branch**: `staging`
- **Workflow**: `.github/workflows/deploy-staging.yml`
- **Environment**: `github-pages-staging` (GitHub deployment environment)
- **Purpose**: Preview and test changes before going to production
- **Visual Indicator**: Orange warning banner at the top of every page
- **Note**: Deployments to staging will temporarily replace the production site. To restore production, redeploy from main.

## How to Use

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
- Deploys to production GitHub Pages environment
- No visual indicators (clean production site)

### Staging Workflow (`deploy-staging.yml`)
- Triggered by pushes to `staging` branch
- Deploys to staging GitHub Pages environment
- Adds orange warning banner to indicate staging
- Can be cancelled if newer push comes in

## Benefits

✅ **No spam commits to main**: Test on staging branch first, only merge when ready
✅ **Safe experimentation**: Break things on staging branch, not production
✅ **Visual distinction**: Orange banner clearly shows staging deployment
✅ **Easy rollback**: Keep main branch stable, redeploy to restore production
✅ **Workflow testing**: Test the entire build and deployment process before production
✅ **Build validation**: Ensure no errors before merging to main

**Note**: Since GitHub Pages (with GitHub Actions source) can only have one active deployment at the same URL, staging and production cannot coexist simultaneously. Staging temporarily replaces production until you redeploy from main. This is still valuable for testing the deployment process and catching build errors before they reach the main branch.

## GitHub Pages Configuration

To enable both production and staging environments:

1. Go to Settings → Pages
2. Source should be set to "GitHub Actions"
3. GitHub will create separate deployment environments automatically:
   - `github-pages` for production (from main branch)
   - `github-pages-staging` for staging (from staging branch)

**Important**: Both environments will deploy to the same GitHub Pages URL. However, GitHub creates separate "environments" in the repository that you can configure with different protection rules and secrets. The staging deployment will **replace** the production deployment on the Pages URL when you push to staging. To see production again, redeploy from main.

**Recommended Setup for True Separate URLs**:
For truly separate staging and production URLs, you would need:
- A separate repository for staging, OR
- Deploy staging to a subdirectory or different branch in Pages settings

The current implementation provides a workflow for testing deployments before promoting to main, but both deploy to the same URL. This is useful for:
- Testing the build process
- Verifying workflows work correctly  
- Checking deployment logs
- Ensuring no build errors before merging to main

## Troubleshooting

**Q: I pushed to staging but nothing happened**
- Check the Actions tab for workflow runs
- Ensure the workflow file exists at `.github/workflows/deploy-staging.yml`
- Check if there are any errors in the workflow run

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
