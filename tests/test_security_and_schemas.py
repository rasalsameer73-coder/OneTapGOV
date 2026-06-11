from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.schemas.auth import RegisterRequest
from app.schemas.eligibility import RuleExpression


def test_password_hashing_and_token_round_trip():
    encoded = hash_password("StrongPassword123")
    assert encoded.startswith("scrypt$")
    assert verify_password("StrongPassword123", encoded)
    assert not verify_password("wrong", encoded)
    assert not verify_password("password", "invalid")

    user_id = uuid4()
    access, expires_in = create_access_token(user_id, "citizen")
    payload = decode_token(access, "access")
    assert payload["sub"] == str(user_id)
    assert expires_in > 0

    refresh, token_hash, expires_at = create_refresh_token(user_id, uuid4())
    refresh_payload = decode_token(refresh, "refresh")
    assert token_hash == hash_token(refresh_payload["jti"])
    assert expires_at.tzinfo is not None
    with pytest.raises(ValueError, match="Expected a access token"):
        decode_token(refresh, "access")


def test_password_policy_and_rule_schema():
    with pytest.raises(ValidationError):
        RegisterRequest(email="citizen@example.com", password="alllowercase12", name="Citizen")
    valid = RegisterRequest(
        email="citizen@example.com", password="StrongPassword12", name="Citizen"
    )
    assert str(valid.email) == "citizen@example.com"
    expression = RuleExpression.model_validate(
        {"all": [{"condition": {"field": "profile.income", "operator": "lt", "value": 200000}}]}
    )
    assert expression.all
    with pytest.raises(ValidationError):
        RuleExpression.model_validate({"all": [], "any": []})

