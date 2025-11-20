from __future__ import annotations

import logging
import sys


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    
    logging.getLogger("app").setLevel(logging.INFO)
    logging.getLogger("app.infrastructure.store").setLevel(logging.INFO)
    
    logging.getLogger("psycopg").setLevel(logging.INFO)
    logging.getLogger("psycopg.pool").setLevel(logging.DEBUG)
    
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

