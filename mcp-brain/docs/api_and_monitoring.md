# API & Monitoring

### API Layer (`/api`)
The FastAPI communication layer. Expects to be utilized by CLI controls, a UI dashboard, or webhook events.
- Endpoints like `/pipeline/start`, `/pipeline/status`, `/agents/status`, `/system/health`.

### Generator endpoints
- `POST /generator/build`: generate a full template from a market design brief (Phase 3)
- `POST /generator/from-screenshot`: generate UI code from an uploaded screenshot via `screenshot-to-code` (Phase 3.5)
- `GET /generator/templates`: list templates in the registry
- `GET /generator/template/{name}`: get template metadata

### Monitoring Layer (`/monitoring`)
- **Logger (`logger.py`)**: Maintains local or cloud file streams outlining what every pipeline step is doing.
- **Metrics (`metrics.py`)**: Tracks performance: Generation Time API cost, API rate limits, test pass rates.
- **Health Check (`health_check.py`)**: Polling tool ensuring third party APIs and local Redis buffers are active and accessible.
