from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Mapping
from urllib.parse import urlencode


TIMESTAMP_SKEW_SECONDS = 300


@dataclass(frozen=True)
class SignatureInput:
    method: str
    path: str
    query_params: Mapping[str, str] | None
    body: bytes
    timestamp: str
    client_id: str


def canonical_query_string(query_params: Mapping[str, str] | None) -> str:
    if not query_params:
        return ""
    items = sorted((str(key), str(value)) for key, value in query_params.items())
    return urlencode(items)


def canonical_request_string(signature_input: SignatureInput) -> str:
    body_hash = hashlib.sha256(signature_input.body or b"").hexdigest()
    query_string = canonical_query_string(signature_input.query_params)
    return "\n".join(
        [
            signature_input.method.upper(),
            signature_input.path,
            query_string,
            body_hash,
            signature_input.timestamp,
            signature_input.client_id,
        ]
    )


def sign_request(signature_input: SignatureInput, shared_secret: str) -> str:
    message = canonical_request_string(signature_input).encode("utf-8")
    digest = hmac.new(shared_secret.encode("utf-8"), message, hashlib.sha256)
    return digest.hexdigest()


def verify_signature(signature_input: SignatureInput, shared_secret: str, provided_signature: str) -> bool:
    expected_signature = sign_request(signature_input, shared_secret)
    return hmac.compare_digest(expected_signature, provided_signature)
