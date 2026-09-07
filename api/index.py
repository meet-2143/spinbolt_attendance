"""Vercel Python serverless entrypoint.

Vercel's Python runtime detects an ASGI `app` object in this module and serves
it directly - no adapter needed. All actual routes/logic live in backend/app.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app  # noqa: E402

__all__ = ["app"]
