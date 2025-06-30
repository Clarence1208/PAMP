# Security Guidelines for Frontend Deployment

## Secret Management

### ⚠️ Critical Security Warning

**Frontend applications expose all environment variables to the browser.** Any secret stored in frontend environment variables can be viewed by end users. This includes:

- API keys
- AWS credentials
- Database connection strings
- Any `VITE_*` prefixed variables

### Current Implementation

This deployment uses a **compromise approach** where sensitive credentials are stored as Kubernetes secrets but are still exposed to the frontend. This is necessary for direct S3 uploads from the browser but comes with security risks.

## Deployment Options

### Option 1: Using Kubernetes Secrets (Current)

```bash
# Deploy with secrets in values.yaml (NOT RECOMMENDED for production)
helm install pamp-frontend ./front-deployment

# Deploy with external secret values (RECOMMENDED)
helm install pamp-frontend ./front-deployment \
  --set secrets.VITE_S3_SECRET_KEY="your-actual-secret" \
  --set secrets.VITE_S3_ACCESS_KEY="your-actual-access-key"
```