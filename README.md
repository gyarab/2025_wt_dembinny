# Dominik Dembinny's project

This is where I'll do all my work for web technology subject.

> Hi

## Deployment

This project uses a three-environment deployment strategy:
- **Production**: Deployed from `main` branch (clean site)
- **Staging**: Deployed from `staging` branch for testing (orange banner)
- **PR Previews**: Automatic preview for each pull request (purple banner)

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions on how to use these deployment environments.

### Quick Start with PR Previews

1. Create a feature branch and push changes
2. Open a pull request on GitHub
3. Automatic preview is deployed with a unique URL
4. Comment with preview link and QR code appears on your PR
5. Share the preview URL for review and testing
