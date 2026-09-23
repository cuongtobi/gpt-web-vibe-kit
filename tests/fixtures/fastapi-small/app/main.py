from fastapi import FastAPI
from app.services.auth_service import refresh_access_token

app = FastAPI()

@app.post("/refresh")
def refresh():
    return refresh_access_token()
