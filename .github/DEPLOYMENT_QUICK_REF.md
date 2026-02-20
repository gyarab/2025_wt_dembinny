# Quick Reference: Production vs Staging

## Production (main branch)
```bash
git checkout main
git add .
git commit -m "Your changes"
git push origin main
```
→ Deploys to production GitHub Pages

## Staging (staging branch)
```bash
git checkout staging
git add .
git commit -m "Test changes"
git push origin staging
```
→ Deploys to staging environment with warning banner

## Merge Staging to Production
```bash
git checkout main
git merge staging
git push origin main
```

## Environment Differences

| Feature | Production | Staging |
|---------|-----------|---------|
| Branch | `main` | `staging` |
| Warning Banner | ❌ No | ✅ Yes (orange) |
| Workflow File | `static.yml` | `deploy-staging.yml` |
| Environment | `github-pages` | `github-pages-staging` |
| Cancel on New Push | ❌ No | ✅ Yes |
