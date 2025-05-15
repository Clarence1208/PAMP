# PAMP TLS Certificate Management

This Helm chart sets up TLS certificate management for edulor.fr using cert-manager and Let's Encrypt.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- Traefik Ingress Controller already installed
- A publicly accessible domain (edulor.fr) that points to your cluster

## Features

- Installs cert-manager (optional, can be disabled if already installed)
- Creates a Let's Encrypt issuer (staging by default, can be switched to production)
- Issues TLS certificates for specified domains
- Configures Traefik IngressRoutes with TLS
- Patches existing Ingress resources with TLS configuration

## Installing the Chart

First, add the JetStack repository (for cert-manager):

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
```

To install the chart with the release name `pamp-certs`:

```bash
helm install pamp-certs ./cert-deployment
```

## Switching to Production

By default, the chart uses Let's Encrypt's staging environment which doesn't issue trusted certificates but has higher rate limits for testing. To switch to production:

1. Edit values.yaml:
   ```yaml
   issuer:
     production: true
   ```

2. Upgrade the release:
   ```bash
   helm upgrade pamp-certs ./cert-deployment
   ```

## Configuration

### Important Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `cert-manager.enabled` | Whether to install cert-manager | `true` |
| `cert-manager.installCRDs` | Whether to install cert-manager CRDs | `true` |
| `issuer.production` | Use Let's Encrypt production (true) or staging (false) | `false` |
| `issuer.email` | Email for Let's Encrypt notifications | `admin@edulor.fr` |
| `issuer.name` | Name of the certificate issuer | `letsencrypt` |
| `issuer.type` | Type of issuer (ClusterIssuer or Issuer) | `ClusterIssuer` |
| `certificates` | List of certificates to issue | See values.yaml |
| `ingressPatches` | List of ingresses to patch with TLS | See values.yaml |

## Adding More Domains

To add more domains to your certificate, edit the `certificates` section in values.yaml:

```yaml
certificates:
  - name: "edulor-tls"
    domains:
      - "edulor.fr"
      - "www.edulor.fr"
      - "api.edulor.fr"  # Add additional domains here
```

## Troubleshooting

### Checking Certificate Status

```bash
kubectl get certificates -A
```

### Checking Certificate Events

```bash
kubectl describe certificate edulor-tls
```

### Checking Certificate Challenges

```bash
kubectl get challenges -A
```

### Common Issues

1. **DNS not configured correctly**: Ensure your domain points to your cluster's public IP
2. **Rate limiting**: Let's Encrypt has rate limits, especially on the production environment
3. **HTTP challenge failure**: Ensure Traefik is properly configured to expose the /.well-known/acme-challenge/ path

## Uninstalling the Chart

```bash
helm delete pamp-certs
```

**Note**: This won't delete the secrets containing the certificates. To delete them:

```bash
kubectl delete secret edulor-tls-cert
``` 