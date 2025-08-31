import pyotp

def get2FACode(secretKey: str) -> str:
    return pyotp.TOTP(secretKey).now()
