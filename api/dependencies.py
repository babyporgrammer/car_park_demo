from fastapi import Header, HTTPException, Depends
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


VALID_KEYS = os.getenv("VALID_API_KEYS", "").split(",")

def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """
    check if the provided API key is valid.
    """
    if x_api_key not in VALID_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
