# app/firebase.py
import firebase_admin
from firebase_admin import credentials, auth
from app.config import Settings

settings = Settings()
cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)


def verify_token(token: str):
    # allow small clock skew so "token used too early" doesn't blow up
    return auth.verify_id_token(token, clock_skew_seconds=300)
