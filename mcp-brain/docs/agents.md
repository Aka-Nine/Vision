# Agent System (`/agents`)

The platform's execution layer. Every agent inherits from `BaseAgent` and handles a highly specific domain requirement:

1. **Market Agent (`market_agent.py`)**: Discovering trend data, analyzing demand on marketplaces, and organizing references.
2. **Generation Agent (`generation_agent.py`)**: The primary LLM coder. Takes references and creates template source code and UI assets.
3. **Testing Agent (`testing_agent.py`)**: Ensures quality layout via automated UI tests (integrates with Playwright to spin up headless browsers).
4. **Publishing Agent (`publishing_agent.py`)**: Bundles template zips and generates promotional structures for the final product upload.
5. **Storage Agent (`storage_agent.py`)**: Strictly manages datasets, file compression, cloud uploads, and bridging to your local network.
