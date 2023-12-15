import secrets, jwt, datetime
from datetime import datetime, timedelta


#-------------------------#

access_secret_key = secrets.token_hex(32)
refresh_secret_key = secrets.token_hex(32)

username = 'BlesK'
scopes = ['read', 'write']

issued_at = datetime.utcnow()
access_expiration = issued_at + timedelta(minutes=1)
refresh_expiration = issued_at + timedelta(hours=1)

refresh_payload = {
    'sub': username,
    'exp': refresh_expiration,
    'iat': issued_at,
    'scopes': scopes
}

access_payload = {
    'sub': username,
    'exp': access_expiration,
    'iat': issued_at,
    'scopes': scopes
}

#-------------------------#

def generate_token(payload, secret_key):
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

def decode_token(token, secret_key):
    try:
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return "token is expired"
    except jwt.InvalidTokenError:
        return "invalid token"

#-------------------------#

access_token = generate_token(access_payload, access_secret_key)
refresh_token = generate_token(refresh_payload, refresh_secret_key)

dec_access_token = decode_token(access_token, access_secret_key)
dec_refresh_token = decode_token(refresh_token, refresh_secret_key)

print(f'\naccess_secret_key: {access_secret_key} \n\nrefresh_secret_key: {refresh_secret_key} \n\naccess_token: {access_token} \n\nrefresh_token: {refresh_token}\n')
print(f'decoded access_token: {dec_access_token} \n\ndecoded refresh_token: {dec_refresh_token}\n')
