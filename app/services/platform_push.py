from __future__ import annotations

from typing import Any

import httpx

from app.core.security import SignatureInput, sign_request
from app.core.settings import get_settings


async def post_signed_json(url: str | None, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    if not url:
        return {"delivered": False, "reason": "url_not_configured"}

    body = httpx.Request("POST", url, json=payload).read()
    signature_input = SignatureInput(
        method="POST",
        path=path,
        query_params={},
        body=body,
        timestamp="0",
        client_id=settings.hmac_client_id,
    )
    headers = {
        "X-Client-Id": settings.hmac_client_id,
        "X-Timestamp": "0",
        "X-Signature": sign_request(signature_input, settings.hmac_shared_secret),
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(url, json=payload, headers=headers)
    return {"delivered": response.is_success, "status_code": response.status_code, "text": response.text}


async def push_approved_quiz(url: str | None, payload: dict[str, Any]) -> dict[str, Any]:
    return await post_signed_json(url, "/webhooks/quizzes/push", payload)


async def push_results(url: str | None, payload: dict[str, Any]) -> dict[str, Any]:
    return await post_signed_json(url, "/webhooks/attempts/graded", payload)
