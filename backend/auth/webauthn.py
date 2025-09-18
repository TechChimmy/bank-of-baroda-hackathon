from __future__ import annotations

import base64
from typing import Dict, Any, List

from fido2.server import Fido2Server
from fido2.webauthn import (
    PublicKeyCredentialRpEntity,
    PublicKeyCredentialUserEntity,
    PublicKeyCredentialDescriptor,
)
from fido2 import cbor
from db import database
from db import models

# Relying Party configuration
RP_ID = "localhost"
RP_NAME = "Bank Hackathon"
ORIGIN = "http://localhost:3000"

rp = PublicKeyCredentialRpEntity(id=RP_ID, name=RP_NAME)
server = Fido2Server(rp, attestation="none")

# In-memory state stores (ephemeral)
_registration_state: Dict[str, Any] = {}
_authenticate_state: Dict[str, Any] = {}


def b64url_encode(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


async def list_user_credentials(user_id: int) -> List[Dict[str, Any]]:
    query = models.webauthn_credentials.select().where(models.webauthn_credentials.c.user_id == user_id)
    rows = await database.fetch_all(query)
    return [dict(r) for r in rows]


async def begin_registration(user_id: int, username: str) -> Dict[str, Any]:
    user = PublicKeyCredentialUserEntity(
        id=username.encode("utf-8"),  # stable per user
        name=username,
        display_name=username,
    )

    existing = await list_user_credentials(user_id)
    exclude = [
        PublicKeyCredentialDescriptor(type="public-key", id=b64url_decode(c["credential_id"]))
        for c in existing
    ]

    options, state = server.register_begin(
        user,
        exclude_credentials=exclude,
        user_verification="preferred",
        authenticator_selection={
            "residentKey": "preferred",
            "userVerification": "preferred",
            "authenticatorAttachment": "platform",
        },
    )

    # Save state per user
    _registration_state[username] = state

    # Convert binary fields to base64url
    public_key = cbor.decode(cbor.encode(options))  # deep copy-like
    public_key["challenge"] = b64url_encode(public_key["challenge"])
    if "user" in public_key and isinstance(public_key["user"].get("id"), (bytes, bytearray)):
        public_key["user"]["id"] = b64url_encode(public_key["user"]["id"])
    if "excludeCredentials" in public_key:
        for cred in public_key["excludeCredentials"]:
            if isinstance(cred.get("id"), (bytes, bytearray)):
                cred["id"] = b64url_encode(cred["id"])

    return public_key


async def finish_registration(username: str, client_data_json_b64: str, attestation_object_b64: str, user_id: int) -> Dict[str, Any]:
    state = _registration_state.get(username)
    if not state:
        raise ValueError("Registration state not found")

    client_data_json = b64url_decode(client_data_json_b64)
    attestation_object = b64url_decode(attestation_object_b64)

    auth_data = server.register_complete(state, client_data_json, attestation_object)

    cred_id = b64url_encode(auth_data.credential_id)
    public_key = b64url_encode(auth_data.credential_public_key)
    sign_count = auth_data.sign_count
    aaguid = b64url_encode(auth_data.aaguid)

    # Store in DB
    query = models.webauthn_credentials.insert().values(
        user_id=user_id,
        credential_id=cred_id,
        public_key=public_key,
        sign_count=sign_count,
        aaguid=aaguid,
        fmt=None,
        transports=None,
        created_at=None,
    )
    await database.execute(query)

    # cleanup
    _registration_state.pop(username, None)

    return {"registered": True, "credential_id": cred_id}


async def begin_authentication(user_id: int, username: str) -> Dict[str, Any]:
    creds = await list_user_credentials(user_id)
    allow = [
        PublicKeyCredentialDescriptor(type="public-key", id=b64url_decode(c["credential_id"]))
        for c in creds
    ]

    options, state = server.authenticate_begin(allow_credentials=allow, user_verification="preferred")

    _authenticate_state[username] = {
        "state": state,
        "keys": {c["credential_id"]: c for c in creds},
    }

    request_options = cbor.decode(cbor.encode(options))
    request_options["challenge"] = b64url_encode(request_options["challenge"])
    if "allowCredentials" in request_options:
        for cred in request_options["allowCredentials"]:
            if isinstance(cred.get("id"), (bytes, bytearray)):
                cred["id"] = b64url_encode(cred["id"])

    return request_options


async def finish_authentication(username: str, credential_id_b64: str, client_data_json_b64: str, authenticator_data_b64: str, signature_b64: str) -> Dict[str, Any]:
    st = _authenticate_state.get(username)
    if not st:
        raise ValueError("Authentication state not found")

    state = st["state"]
    creds_map = st["keys"]

    cred_id = b64url_decode(credential_id_b64)
    client_data_json = b64url_decode(client_data_json_b64)
    authenticator_data = b64url_decode(authenticator_data_b64)
    signature = b64url_decode(signature_b64)

    # Build mapping id->public key bytes for server
    from fido2 import cbor
    from fido2.webauthn import AuthenticatorData

    stored_cred = None
    for k, v in creds_map.items():
        if b64url_decode(k) == cred_id:
            stored_cred = v
            break

    if not stored_cred:
        raise ValueError("Unknown credential")

    public_key = b64url_decode(stored_cred["public_key"])  # bytes

    server.authenticate_complete(
        state=state,
        credential_id=cred_id,
        client_data=client_data_json,
        auth_data=authenticator_data,
        signature=signature,
        public_key=public_key,
        user_handle=None,
    )

    # Optionally update sign_count in DB is handled by library; we can increment if returned
    # Cleanup
    _authenticate_state.pop(username, None)

    return {"authenticated": True}
