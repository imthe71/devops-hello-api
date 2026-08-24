# Hello DevOps API

A minimal FastAPI application for a GitOps CI/CD demonstration.

Endpoints:

- `GET /` — deployment version and Pod hostname
- `GET /config-status` — confirms whether runtime parameters were loaded from an environment variable or CSI-mounted file; secret values are never returned
- `GET /healthz` — liveness/startup health check
- `GET /readyz` — readiness health check

The GitHub Actions workflow runs tests, pushes a Git SHA-tagged image to GHCR, then updates the Helm `image.tag` in the separate GitOps repository.
