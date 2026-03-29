# Core Components (`/core`)

These modules are the central nervous system of the MCP Brain:

- **Orchestrator (`orchestrator.py`)**: The primary coordinator. Initializes agents, starts/stops pipelines across the entire suite, and handles task failures.
- **Pipeline Engine (`pipeline_engine.py`)**: Manages workflow chains. Ensures dependencies are met (e.g., Generation occurs *only* if Market Research succeeds).
- **Event Bus (`event_bus.py`)**: A publish/subscribe event system. If the `Testing Agent` emits `test_passed`, the Orchestrator catches it and fires off the `Publishing Agent`.
- **Task Queue (`task_queue.py`)**: Async background task manager (can be powered by Redis or Celery). Prevents the FastAPI application from blocking while LLMs take 2+ minutes to generate data.
