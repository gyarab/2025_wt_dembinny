# Quick Reference: Production vs Staging vs PR Previews

## PR Preview (Recommended for Pull Requests)
```bash
# 1. Create feature branch
git checkout -b feature/my-feature
git add .
git commit -m "Add feature"
git push origin feature/my-feature

# 2. Create PR on GitHub
# → Automatic preview deployed
# → Comment with link posted on PR
# → URL: https://gyarab.github.io/2025_wt_dembinny/pr-preview/pr-[NUMBER]/

# 3. Update PR (preview auto-updates)
git add .
git commit -m "Update feature"
git push origin feature/my-feature

# 4. Merge PR → Preview auto-deleted
```

## Production (main branch)
```bash
git checkout main
git add .
git commit -m "Your changes"
git push origin main
```
→ Deploys to production GitHub Pages (root URL)

## Staging (staging branch)
```bash
git checkout staging
git add .
git commit -m "Test changes"
git push origin staging
```
→ Deploys to staging (temporarily replaces production)

## Merge Staging to Production
```bash
git checkout main
git merge staging
git push origin main
```

## Environment Comparison

| Feature | Production | Staging | PR Preview |
|---------|-----------|---------|------------|
| Branch | `main` | `staging` | Any (via PR) |
| URL | Root | Root (temp) | `/pr-preview/pr-[N]/` |
| Banner | ❌ None | 🟠 Orange | 🟣 Purple |
| Workflow | `static.yml` | `deploy-staging.yml` | `deploy-pr-preview.yml` |
| Deployment | `gh-pages` root | `gh-pages` root | `gh-pages/pr-preview/` |
| Multiple Simultaneous | ❌ No | ❌ No | ✅ Yes |
| Auto Comment | ❌ No | ❌ No | ✅ Yes (with QR code) |
| Auto Cleanup | ❌ N/A | ❌ N/A | ✅ Yes (on PR close) |
| Best For | Final release | Pre-release testing | PR review & testing |
