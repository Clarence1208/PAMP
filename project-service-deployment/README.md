# PAMP Project Service Deployment

This Helm chart deploys the PAMP Project Service API to Kubernetes, providing student batch management functionality for the PAMP platform.

## Overview

The PAMP Project Service is a NestJS-based API that manages student batches (promotions) and integrates with the PAMP authentication service. It provides endpoints for creating, managing, and querying student batches with full CRUD operations.

## Features

- **Student Batch Management**: Create, update, delete, and query student batches
- **PostgreSQL Database**: Persistent data storage with automatic migrations
- **Authentication Integration**: Integrates with PAMP Auth Service
- **Swagger Documentation**: API documentation available at `/swagger-ui`
- **Health Checks**: Liveness and readiness probes for high availability
- **Auto-scaling**: Horizontal Pod Autoscaler support
- **Ingress Support**: HTTPS access via Traefik with automatic TLS certificates

## Prerequisites

- Kubernetes 1.19+
- Helm 3.8+
- Traefik ingress controller (for ingress)
- TLS certificate for `projects.edulor.fr`

## Installation

### 1. Add Dependencies

First, update the Helm dependencies:

```bash
helm dependency update
```

### 2. Deploy the Chart

```bash
helm install pamp-project-service . -n pamp-platform --create-namespace
```

Or with custom values:

```bash
helm install pamp-project-service . -n pamp-platform -f custom-values.yaml
```

### 3. Upgrade an Existing Release

```bash
helm upgrade pamp-project-service . -n pamp-platform
```

## Configuration

### Database Configuration

The chart includes PostgreSQL as a dependency. Database configuration:

```yaml
postgresql:
  enabled: true
  auth:
    username: postgres
    password: postgres
    database: pamp_projects
  service:
    port: 5432
```

### Environment Variables

Key environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgres://postgres:postgres@pamp-project-service-postgresql:5432/pamp_projects` |
| `NODE_ENV` | Node.js environment | `production` |
| `JWT_SECRET` | JWT signing secret | `change-me-in-production` |
| `LOG_LEVEL` | Application log level | `info` |

### Service Configuration

```yaml
service:
  type: ClusterIP
  port: 3000
```

### Ingress Configuration

```yaml
ingress:
  enabled: true
  className: "traefik"
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web,websecure
  hosts:
    - host: projects.edulor.fr
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: projects-edulor-tls-cert
      hosts:
        - projects.edulor.fr
```

### Resource Limits

```yaml
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

## Values

### Common Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Container image repository | `ghcr.io/mil0w0/pamp-project-api` |
| `image.tag` | Container image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `Always` |
| `fullnameOverride` | Override the full name | `pamp-project-service` |

### Security Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `serviceAccount.create` | Create service account | `true` |
| `podSecurityContext` | Pod security context | `{}` |
| `securityContext` | Container security context | `{}` |

### Autoscaling Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `autoscaling.enabled` | Enable HPA | `false` |
| `autoscaling.minReplicas` | Minimum replicas | `1` |
| `autoscaling.maxReplicas` | Maximum replicas | `3` |
| `autoscaling.targetCPUUtilizationPercentage` | Target CPU % | `80` |

## API Endpoints

The deployed service provides the following main endpoints:

- `GET /` - Health check endpoint
- `GET /swagger-ui` - API documentation
- `GET /student-batches` - List all student batches
- `POST /student-batches` - Create a new student batch
- `GET /student-batches/:id` - Get a specific student batch
- `PATCH /student-batches/:id` - Update a student batch
- `DELETE /student-batches/:id` - Delete a student batch

## Monitoring

### Health Checks

The deployment includes both liveness and readiness probes:

```yaml
livenessProbe:
  httpGet:
    path: /
    port: http
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /
    port: http
  initialDelaySeconds: 5
  periodSeconds: 10
```

### Logs

View application logs:

```bash
kubectl logs -l app.kubernetes.io/name=project-service-deployment -n pamp-platform
```

### Status

Check deployment status:

```bash
kubectl get pods -l app.kubernetes.io/name=project-service-deployment -n pamp-platform
```

## Development

### Local Development

For local development with Docker:

```bash
cd ../pamp-project-api
docker-compose up --build
```

The API will be available at `http://localhost:3000`

### Testing

Run the test suite:

```bash
cd ../pamp-project-api
npm test
```

## Database Schema

The service manages the following main entity:

### StudentBatch Entity

```sql
CREATE TABLE student_batch (
    id UUID PRIMARY KEY,
    state VARCHAR DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    name VARCHAR NOT NULL,
    tags VARCHAR DEFAULT '',
    students VARCHAR DEFAULT ''
);
```

## Integration

### Authentication Service

The project service integrates with the PAMP Auth Service:

- **Authentication endpoint**: `https://auth.edulor.fr`
- **User management**: Fetches user details for student batch members
- **JWT validation**: Validates tokens issued by the auth service

### Dependencies

- **PostgreSQL**: Primary database for student batch data
- **PAMP Auth Service**: User authentication and management
- **Traefik**: Ingress controller for HTTPS termination

## Troubleshooting

### Common Issues

1. **Pod not starting**: Check logs and ensure database is accessible
2. **Database connection errors**: Verify PostgreSQL service is running
3. **Ingress not working**: Check TLS certificate and Traefik configuration
4. **Auth integration issues**: Verify auth service is accessible

### Debug Commands

```bash
# Check pod status
kubectl get pods -n pamp-platform

# View pod logs
kubectl logs <pod-name> -n pamp-platform

# Check services
kubectl get svc -n pamp-platform

# Check ingress
kubectl get ingress -n pamp-platform

# Check configmaps and secrets
kubectl get configmap,secret -n pamp-platform
```
## Authors

- Loriane HILDERAL
- Clarence HIRSCH
- Malik LAFIA