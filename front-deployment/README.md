# PAMP Frontend Deployment

This Helm chart deploys the PAMP Frontend application on a Kubernetes cluster.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- Traefik Ingress Controller (for ingress functionality)

## Installing the Chart

To install the chart with the release name `pamp-frontend`:

```bash
helm install pamp-frontend ./front-deployment
```

The command deploys the PAMP Frontend on the Kubernetes cluster with the default configuration.

## Uninstalling the Chart

To uninstall/delete the `pamp-frontend` deployment:

```bash
helm delete pamp-frontend
```

## Configuration

The following table lists the configurable parameters of the PAMP Frontend chart and their default values.

| Parameter                | Description             | Default        |
| ------------------------ | ----------------------- | -------------- |
| `replicaCount`           | Number of replicas      | `1`            |
| `image.repository`       | Image repository        | `ghcr.io/clarence1208/pamp-frontend` |
| `image.pullPolicy`       | Image pull policy       | `Always`       |
| `image.tag`              | Image tag               | `latest`       |
| `service.type`           | Service type            | `ClusterIP`    |
| `service.port`           | Service port            | `80`           |
| `ingress.enabled`        | Enable ingress          | `true`         |
| `ingress.className`      | Ingress class name      | `traefik`      |
| `ingress.hosts`          | Ingress hosts           | `[{host: edulor.fr, paths: [{path: /, pathType: Prefix}]}]` |
| `resources.limits.cpu`   | CPU limits              | `300m`         |
| `resources.limits.memory`| Memory limits           | `256Mi`        |
| `resources.requests.cpu` | CPU requests            | `100m`         |
| `resources.requests.memory` | Memory requests      | `128Mi`        |
| `env`                    | Environment variables   | `{NODE_ENV: "production", VITE_AUTH_API_URL: "https://auth.edulor.fr"}` |
| `secrets`                | Sensitive environment variables | `{VITE_S3_SECRET_KEY: "your-secret"}` |
| `configData`             | Configuration data      | NGINX configurations |

## Customization

### Environment Variables

You can customize the environment variables by modifying the `env` section in the `values.yaml` file:

```yaml
env:
  NODE_ENV: "production"
  VITE_API_URL: "https://edulor.fr/user-api"
  # Add your custom environment variables here
```

### NGINX Configuration

NGINX configuration is managed through the `configData` section:

```yaml
configData:
  NGINX_CLIENT_MAX_BODY_SIZE: "10m"
  NGINX_PROXY_CONNECT_TIMEOUT: "60s"
  NGINX_PROXY_SEND_TIMEOUT: "60s"
  NGINX_PROXY_READ_TIMEOUT: "60s"
```

## Secret Management

⚠️ **Security Warning**: This chart handles sensitive credentials like AWS S3 keys. See [SECURITY.md](./SECURITY.md) for detailed security guidelines and best practices.

### Quick Setup for Development

```bash
helm install pamp-frontend ./front-deployment \
  --set secrets.VITE_S3_SECRET_KEY="your-s3-secret-key"
```

## Ingress Configuration

The frontend is configured to be accessible through an Ingress resource. By default, it's configured to use Traefik as the ingress controller with the host `edulor.fr`. 