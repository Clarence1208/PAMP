# PAMP Auth Service Helm Chart

This Helm chart deploys the PAMP Authentication Service and its dependencies.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- PV provisioner support in the underlying infrastructure (for PostgreSQL persistence)

## Installing the Chart

To install the chart with the release name `pamp-auth`:

```bash
# Add the Bitnami repository for PostgreSQL dependency
  helm repo add bitnami https://charts.bitnami.com/bitnami

# Update repositories
  helm repo update

# Install the chart
  helm install pamp-auth-service ./auth-deployment
```

The command deploys the PAMP Auth Service on the Kubernetes cluster with default configuration. The [Parameters](#parameters) section lists the parameters that can be configured during installation.

## Deploying the last version

To deploy the latest version of the chart, you can use the following command:

```bash
  kubectl rollout restart deployment pamp-auth-service \
  -n default
```

get the pods of the service:

```bash
  kubectl get pods --namespace default -l "app.kubernetes.io/name=auth-deployment,app.kubernetes.io/instance=pamp-auth-service"
```

logs of a pod:

```bash
  kubectl logs pamp-auth-service-5d599fc5bd-hbhfk
```

## Uninstalling the Chart

To uninstall/delete the `pamp-auth` deployment:

```bash
  helm uninstall pamp-auth-service
```

## Parameters

### Common parameters

| Name                | Description                                                                           | Value           |
|---------------------|---------------------------------------------------------------------------------------|-----------------|
| `replicaCount`      | Number of replicas                                                                    | `1`             |
| `image.repository`  | Image repository                                                                      | `pamp-auth-service` |
| `image.tag`         | Image tag                                                                             | `latest`        |
| `image.pullPolicy`  | Image pull policy                                                                     | `IfNotPresent`  |
| `nameOverride`      | String to partially override the release name                                         | `""`            |
| `fullnameOverride`  | String to fully override the release name                                             | `pamp-auth-service` |

### Service parameters

| Name                       | Description                                                      | Value       |
|----------------------------|------------------------------------------------------------------|-------------|
| `service.type`             | Service type                                                     | `ClusterIP` |
| `service.port`             | Service port                                                     | `3000`      |

### Database parameters

| Name                          | Description                                                    | Value        |
|-------------------------------|----------------------------------------------------------------|--------------|
| `postgresql.enabled`          | Deploy PostgreSQL container                                    | `true`       |
| `postgresql.auth.username`    | PostgreSQL username                                            | `postgres`   |
| `postgresql.auth.password`    | PostgreSQL password                                            | `postgres`   |
| `postgresql.auth.database`    | PostgreSQL database name                                       | `pamp_auth`  |

### Environment variables

| Name                          | Description                                                    | Value        |
|-------------------------------|----------------------------------------------------------------|--------------|
| `env.DATABASE_URL`            | Database connection URL                                        | `postgres://postgres:postgres@{{ .Release.Name }}-postgresql:5432/pamp_auth` |

### Secret values

| Name                          | Description                                                    | Value        |
|-------------------------------|----------------------------------------------------------------|--------------|
| `secrets.JWT_SECRET`          | JWT signing secret (change in production)                      | `change-me-in-production` |

## Configuration

The following table lists the configurable parameters of the PAMP Auth Service chart and their default values.

### ConfigMap values

| Name                          | Description                                                    | Value        |
|-------------------------------|----------------------------------------------------------------|--------------|
| `configData.LOG_LEVEL`        | Log level for the application                                  | `info`       |
| `configData.RUST_LOG`         | Rust logging configuration                                     | `info`       |

## Persistence

The PostgreSQL image stores the database data at the `/var/lib/postgresql/data` path of the container.

The chart mounts a Persistent Volume at this location. The volume is created using dynamic volume provisioning. 