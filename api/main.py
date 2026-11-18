"""
ASGI Entrypoint Alias for Render (`uvicorn api.main:app` or `uvicorn server:app`).
"""

from server import app  # noqa: F401
