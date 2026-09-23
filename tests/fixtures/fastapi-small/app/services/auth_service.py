from app.security.token import decode_refresh_token

def refresh_access_token():
    payload = decode_refresh_token("token")
    return {"access_token": payload["sub"]}
