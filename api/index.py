# Vercel Serverless entry for FastAPI
# Exposes the FastAPI ASGI app at module-level variable `app` so @vercel/python can serve it.
# All routes are included via vercel.json routing to this file.

from app.main import app  # noqa: F401  # Vercel detects this ASGI app
