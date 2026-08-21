# Hello DevOps API

A minimal FastAPI application for a GitOps CI/CD demonstration.

Endpoints:

- `GET /` — deployment version and Pod hostname
- `GET /healthz` — liveness/startup health check
- `GET /readyz` — readiness health check

The GitHub Actions workflow runs tests, pushes a Git SHA-tagged image to GHCR, then updates the Helm `image.tag` in the separate GitOps repository.
