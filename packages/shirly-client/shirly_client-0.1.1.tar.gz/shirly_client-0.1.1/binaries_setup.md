# Shirly Scheduler Binaries

This guide explains how to install and operate the `scheduler-api`, `scheduler-worker`, and dashboard binaries that ship with Shirly release bundles. It is intended for operators and client developers who want a working backend before integrating any SDK.

## 1. Download & Verify

Each release bundle is packaged as:

- `shirly-<target>-<timestamp>.tar.gz`
- `shirly-<target>-<timestamp>.tar.gz.sha256`

Steps:

```bash
curl -LO https://example.com/releases/shirly-x86_64-unknown-linux-gnu-20251111T182138Z.tar.gz
curl -LO https://example.com/releases/shirly-x86_64-unknown-linux-gnu-20251111T182138Z.tar.gz.sha256

sha256sum -c shirly-x86_64-unknown-linux-gnu-20251111T182138Z.tar.gz.sha256
```

## 2. Extract & Layout

```bash
tar -xf shirly-x86_64-unknown-linux-gnu-20251111T182138Z.tar.gz -C /opt
cd /opt/shirly-x86_64-unknown-linux-gnu-20251111T182138Z
```

Inside you’ll find:

- `bin/scheduler-api`
- `bin/scheduler-worker`
- `config.example.toml`
- `dashboard/dist/` (static UI)
- `docs/` (client-specific guides)

Copy `config.example.toml` to `config.toml` and adjust paths, credentials, and security settings as needed.

> All commands below assume you stay in the extracted release directory so the binaries can locate `config.toml`.

## 3. Required Services

| Component      | Requirement                                           |
|----------------|--------------------------------------------------------|
| Datastore      | Redis/Dragonfly endpoint, e.g. `redis://localhost:6379` |
| Cache storage  | Writable directory for `SCHEDULER_CACHE__PATH`         |
| Networking     | Open ports: API (`8080` default) and metrics (`9090`)  |

Ensure the datastore is running before starting Shirly components:

```bash
docker run -d --name dragonfly -p 6379:6379 docker.dragonflydb.io/dragonflydb/dragonfly
```

## 4. Start the API Gateway

```bash
export DRAGONFLY_URL=redis://localhost:6379
export SCHEDULER_CACHE__PATH=/var/lib/shirly/cache
mkdir -p "${SCHEDULER_CACHE__PATH}"

./bin/scheduler-api
```

Key environment variables:

- `DRAGONFLY_URL` – Redis/Dragonfly connection string
- `SCHEDULER_CACHE__PATH` – persistent cache location
- `LOG_LEVEL` / `RUST_LOG` – optional logging overrides

The API listens on `0.0.0.0:8080` by default with the REST surface documented in `docs/api.md`. Job priorities are specified via the optional `priority` field (`"normal"` by default, `"critical"` for the high-priority stream).

## 5. Start Workers

Run as many workers as needed; each should have a unique ID:

```bash
export WORKER_ID=worker-1
export DRAGONFLY_URL=redis://localhost:6379
export SCHEDULER_CACHE__PATH=/var/lib/shirly/cache

./bin/scheduler-worker
```

Important settings:

- `worker.concurrency` (in `config.toml`) – max simultaneous jobs
- `worker.poll_interval_ms` – queue polling cadence
- `worker.heartbeat_interval_secs` – worker health updates

Both binaries read `config.toml` first, then environment variables override specific fields (`SCHEDULER_WORKER__CONCURRENCY`, etc.).

## 6. Dashboard (Optional)

Serve the bundled static assets:

```bash
cd dashboard/dist
npx serve .
```

Set `VITE_API_BASE_URL` in `dashboard/dist/config.json` (or equivalent) so the UI points at your API endpoint. The dashboard provides controls for submitting jobs, monitoring worker heartbeats, and viewing queue depth.

## 7. Smoke Test

With the API and at least one worker running:

```bash
curl -X POST http://localhost:8080/api/v1/jobs \
  -H 'Content-Type: application/json' \
  -d '{
        "priority": "critical",
        "payload": {"operation": "ping"}
      }'
```

Follow up with:

```bash
curl http://localhost:8080/api/v1/jobs/<job_id>
```

State transitions:

1. `pending` – accepted by API
2. `running` – claimed by worker
3. `completed` or `failed` – final state

Omit the `priority` field (or set it to `"normal"`) to use the standard queue; use `"critical"` when you need the high-priority stream queue.

## 8. Operational Tips

- Metrics exposed at `http://localhost:8080/metrics` (Prometheus format).
- Health endpoint `GET /api/v1/admin/health` to verify cache/datastore connectivity.
- Logs use structured JSON by default; override with `RUST_LOG=info,shirly=debug`.
- For production, run API and workers under a supervisor/systemd with restart policies.

Once the backend is healthy, proceed to client-specific instructions in the subfolder `release_docs/clients/`. Each client guide assumes the API is reachable and workers are processing jobs as described above.

