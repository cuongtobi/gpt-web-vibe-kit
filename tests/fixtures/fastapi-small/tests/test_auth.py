from app.services.auth_service import refresh_access_token

def test_refresh_after_session_expiry():
    assert refresh_access_token()["access_token"] == "user-1"
