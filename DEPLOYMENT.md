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
- **URL**: Available after first deployment (shown in Actions output)
- **Purpose**: Preview changes before going to production
- **Visual Indicator**: Orange warning banner at the top of every page

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
   - Visit the staging URL (shown in the Actions output)
   - You'll see an orange warning banner indicating it's staging
   - Test all your changes

6. **If everything looks good, merge to main:**
   ```bash
   git checkout main
   git merge staging
   git push origin main
   ```

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

✅ **No spam commits to main**: Test on staging first
✅ **Safe experimentation**: Break things on staging, not production
✅ **Visual distinction**: Orange banner clearly shows staging vs production
✅ **Easy rollback**: Keep main stable, experiment on staging
✅ **Parallel development**: Multiple people can work on staging

## GitHub Pages Configuration

To enable both environments, ensure in your repository settings:

1. Go to Settings → Pages
2. Source should be set to "GitHub Actions"
3. Both environments will deploy to the same Pages URL, but staging uses a different environment

**Note**: The first time you push to staging, you may need to configure the staging environment in Settings → Environments.

## Troubleshooting

**Q: I pushed to staging but nothing happened**
- Check the Actions tab for workflow runs
- Ensure the workflow file exists at `.github/workflows/deploy-staging.yml`
- Check if there are any errors in the workflow run

**Q: How do I find my staging URL?**
- Go to Actions → Select the latest "Deploy staging to Pages" run
- Look for the deployment URL in the output
- Or check Settings → Environments → github-pages-staging

**Q: Can I have multiple staging branches?**
- The current setup uses one staging branch
- You could create additional workflow files for other branches if needed

**Q: How do I delete staging?**
- Simply delete the staging branch: `git push origin --delete staging`
- The staging environment will remain in GitHub but won't be updated
