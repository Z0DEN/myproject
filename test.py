import jwt
from datetime import datetime, timedelta

issued_at = datetime.utcnow()
access_expiration = issued_at + timedelta(minutes=100)
refresh_expiration = issued_at + timedelta(hours=1)


access_payload = {
    "sub": "BlesK",
    "exp": access_expiration,
    "iat": issued_at,
}

key = "123456789secret_key"

def generate_token(payload, secret_key):
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


def decode_token(token, secret_key):
    try:
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        return decoded, 22
    except jwt.ExpiredSignatureError:
        return 14
    except jwt.InvalidTokenError:
        return 15

token = generate_token(access_payload, key)
print(key)
dec_token = decode_token(token, key)


print(token)
print("")
print(dec_token)
