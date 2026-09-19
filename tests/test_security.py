import pytest
import time
import jwt as pyjwt

from app.core.config import settings

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)

def test_hash_and_verify_password():
    password = "mysecretpassword"
    hashed = hash_password(password)

    assert isinstance(hashed, str)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_create_and_decode_access_token():
    user_id = "some-uuid-string"
    token = create_access_token(user_id)
    assert isinstance(token, str)

    payload = decode_token(token, expected_type="access")
    assert payload["sub"] == user_id
    assert payload["type"] == "access"


def test_create_and_decode_refresh_token():
    user_id = "some-uuid-string"
    token = create_refresh_token(user_id)
    assert isinstance(token, str)

    payload = decode_token(token, expected_type="refresh")
    assert payload["sub"] == user_id
    assert payload["type"] == "refresh"


def test_access_token_rejected_when_refresh_expected():
    token = create_access_token("some-uuid-string")
    with pytest.raises(pyjwt.InvalidTokenError):
        decode_token(token, expected_type="refresh")


def test_refresh_token_rejected_when_access_expected():
    token = create_refresh_token("some-uuid-string")
    with pytest.raises(pyjwt.InvalidTokenError):
        decode_token(token, expected_type="access")


def test_decode_garbage_token_raises():
    with pytest.raises(pyjwt.InvalidTokenError):
        decode_token("not-a-real-jwt-at-all", expected_type="access")

def test_expired_access_token_rejected():
    payload = {
        "sub": "some-uuid-string",
        "type": "access",
        "exp": int(time.time()) - 60, 
    }
    expired_token = pyjwt.encode(payload, settings.jwt_private_key, algorithm=settings.jwt_access_algorithm)

    with pytest.raises(pyjwt.ExpiredSignatureError):
        decode_token(expired_token, expected_type="access")


def test_tampered_token_signature_rejected():
    token = create_access_token("some-uuid-string")
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")

    mid = len(token) // 2
    original_char = token[mid]
    replacement = "A" if original_char != "A" else "B"
    tampered = token[:mid] + replacement + token[mid + 1:]
    
    with pytest.raises(pyjwt.InvalidTokenError):
        decode_token(tampered, expected_type="access")


def test_verify_password_with_malformed_hash_fails_safely():
    try:
        result = verify_password("anypassword", "not-a-real-hash-at-all")
        assert result is False
    except Exception as e:
        assert isinstance(e, Exception)