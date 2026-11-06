import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

def get_access_token():
    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": os.getenv("SH_CLIENT_ID"),
            "client_secret": os.getenv("SH_CLIENT_SECRET"),
            "grant_type": "client_credentials"
        },
        timeout=30
    )
    response.raise_for_status()
    return response.json()["access_token"]