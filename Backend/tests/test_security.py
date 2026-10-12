from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hashing_and_jwt():
    password = "StrongTestPassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)
    token = create_access_token("user-1", "student")
    payload = decode_access_token(token)
    assert payload["sub"] == "user-1"
    assert payload["role"] == "student"
