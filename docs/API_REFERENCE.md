# Local read-only HTTP API — `/api/v1`

**Binding:** `127.0.0.1:8765` by default; no external network binding or authentication surface. Imported evidence is private local data. All state-changing HTTP methods return `405`.

| Method | Path | Response |
|---|---|---|
| GET | `/api/v1/health/live` | local process status |
| GET | `/api/v1/health/ready` | state storage readiness |
| GET | `/api/v1/status[?batch_id=...]` | bounded 14-language technical summary |
| GET | `/api/v1/batches` | immutable import metadata, no raw Windows paths |
| GET | `/api/v1/languages[?batch_id=...]` | 14 technical language results |
| GET | `/api/v1/scenarios[?language=Fre&batch_id=...]` | selected 15-intent candidate records |
| GET | `/api/v1/matrix?language=Fre` | 14 signals with canonical gaps explicit |
| GET | `/api/v1/trends?language=Fre` | separate technical candidate trends |
| GET | `/api/v1/report` | persisted report projection, no rescanning |
| GET | `/api/v1/diagnostics` | sanitized ingestion attempt events |

Success envelope: `{"data":..., "meta":{"request_id":"req_...","contract_version":"1.0","generated_at":"...Z"}}`. Failure envelope: `{"error":{"code":"OBS_...","message":"...","request_id":"...","details":{}}}`.

Browser pages `/`, `/app.js`, `/style.css` are local assets. The HTTP server validates Host, returns `Cache-Control: no-store`, CSP, Referrer-Policy and `nosniff`. Source candidate texts are rendered using DOM `textContent` rather than interpreting HTML.

The API never imports a ZIP, compiles GF, writes the RGL, creates a released RuntimeSet or publishes to GitHub. Admin actions remain local CLI/Tkinter operations.
