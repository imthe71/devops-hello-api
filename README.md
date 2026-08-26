# Hello DevOps API

A minimal FastAPI application for a GitOps CI/CD demonstration.

Endpoints:

- `GET /` — deployment version and Pod hostname
- `GET /config-status` — confirms whether runtime parameters were loaded from an environment variable or CSI-mounted file; secret values are never returned
- `GET /db-status` — confirms whether the PostgreSQL configuration is present and reachable; credentials are never returned
- `GET /notes` — lists persisted demonstration notes from PostgreSQL
- `POST /notes` — stores a demonstration note in PostgreSQL, for example `{"content":"UAT persistence verified"}`
- `GET /healthz` — liveness/startup health check
- `GET /readyz` — readiness health check; also reports unready while a configured database is unavailable

The GitHub Actions workflow runs tests, pushes a Git SHA-tagged image to private GHCR, then updates the Helm `image.tag` in the separate GitOps repository. The Helm chart deploys PostgreSQL as a single-replica StatefulSet with a `standard` StorageClass-backed 1Gi PVC in each environment.
