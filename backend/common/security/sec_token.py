import secrets


def generate_secret_token() -> str:
    token = secrets.token_urlsafe()
    return token