# Production release verification

The public health endpoint reports database availability and the deployed Git release:

```json
{
  "status": "ok",
  "release": "<full commit SHA>",
  "service": "aastha-skin-centre-cms"
}
```

Check `https://<host>/healthz/` after each Render deployment and compare `release` with the expected commit on the repository's `main` branch.

The response is marked `Cache-Control: no-store` so a previous deployment value is not reused by browsers or intermediate caches.

A release value of `unknown` means the runtime did not provide `RENDER_GIT_COMMIT` or `GIT_COMMIT`; investigate the service environment before treating the deployment as verified.
