# Hybrid Storage (`/storage`)

Cloud is for active running pipelines, local is for permanent archives.

- **Cloud Storage (`cloud_storage.py`)**: Hosts metadata and temporary files being manipulated by currently active Agents.
- **Local Sync (`local_sync.py`)**: Downloads heavy completed datasets directly to your laptop when available, freeing up expensive cloud space.
- **Compression Service (`compression_service.py`)**: Ensures data synced locally or backed up in cold storage is highly compressed.
- **Metadata Store (`metadata_store.py`)**: Keeps a permanent ledger (database connection) of where all content pieces physically reside.
