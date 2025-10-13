# Setup Guide

## Prerequisites

- Python 3.10+
- Docker & Docker Compose
- PostgreSQL 17 (via Docker)

## Installation

### 1. Clone

```bash
git clone <repository>
cd agent-ltm-persistence-layer
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Database Setup

```bash
docker compose up -d
```

Verify PostgreSQL is running:

```bash
docker exec agent_ltm_postgres psql -U postgres -d agent_ltm -c "SELECT version();"
```

### 4. Environment Variables

```bash
cp env.example .env
```

Edit `.env`:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=agent_ltm
DB_USER=postgres
DB_PASSWORD=postgres
```

## Running

### API Server

```bash
uvicorn ltm.api.app:app --reload
```

### Tests

```bash
pytest
```

## Verification

Check database connection:

```bash
python -c "from ltm.core.database import db; import asyncio; asyncio.run(db.connect()); print('Connected')"
```
