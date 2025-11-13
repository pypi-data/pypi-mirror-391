"""
Doc String

"""
import json
import base64
from time import time
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from .sgn import SGN

__all__ = ["JWT"]

sample_dict = {
    "issuer": "auth-server",
    "subject": "user123",
    "audience": "client-app",
    "duration": 3600,
    "name": "Umesh",
    "roles": ["admin"],
    "scope": "read write"
    # other optional fields...
}

@dataclass
class PLD:
    payload: dict

    @classmethod
    def build(cls, data: dict):
        now = int(time())
        claims = {
            "iss": data.get("issuer", "auth-server"),
            "sub": data.get("subject", "user123"),
            "aud": data.get("audience", "client-app"),
            "exp": now + data.get("duration", 3600),
            "nbf": now,
            "iat": now,
            "jti": f"{int(time() * 1000)}-{data.get('issuer', 'auth-server')}",
            "name": data.get("name", ""),
            "roles": data.get("roles", []),
            "scope": data.get("scope", ""),
            "email": data.get("email", ""),
            "email_verified": data.get("email_verified", False),
            "picture": data.get("picture", ""),
            "given_name": data.get("given_name", ""),
            "family_name": data.get("family_name", ""),
            "locale": data.get("locale", ""),
            "auth_time": data.get("auth_time", now),
            "org": data.get("org", ""),
            "custom": data.get("custom", {})
        }
        return cls(claims)

    
class JWT:
    PLD = PLD
    CURVE_ALG = {
        "secp256r1": "ES256",
        "secp384r1": "ES384",
        "secp521r1": "ES512",
        "secp256k1": "ES256K"
    }

    @classmethod
    def encode(cls, payload: dict, private_key) -> str:
        header = {"alg": cls.jwtalg(private_key), "typ": "JWT"}
        header_b64 = cls.encode_json(header)
        payload_b64 = cls.encode_json(payload)
        signing_input = header_b64 + b"." + payload_b64
        signature = SGN.sign(private_key, signing_input)
        return CMNUtils.to_str(signing_input + b"." + CMNUtils.to_bytes(signature))

    @classmethod
    def decode(cls, token_str: str, public_key, aud: str) -> dict:
        token = CMNUtils.to_bytes(token_str)
        parts = token.split(b'.')
        if len(parts) != 3:
            raise ValueError("Invalid JWT format: expected 3 parts")

        signing_input, signature = b'.'.join(parts[:2]), parts[2]
        SGN.verify(public_key, signature, signing_input)

        header = cls.decode_json(parts[0])
        payload = cls.decode_json(parts[1])

        if header.get("alg") != cls.jwtalg(public_key):
            raise ValueError("Algorithm mismatch during verification")
        if payload.get("aud") != aud:
            raise ValueError("Audience mismatch during verification")

        return payload
    
    @classmethod
    def jwtalg(cls, key):
        if CMNUtils.is_rsa_key(key):
            size = key.key_size
            return f"PS{512 if size >= 4096 else 384 if size >= 3072 else 256}"
        elif CMNUtils.is_ec_key(key):
            return cls.CURVE_ALG.get(key.curve.name, "ES256")
        else:
            raise ValueError("Unsupported key type")

    @classmethod
    def encode_json(cls, obj: dict) -> bytes:
        return CMNUtils.b64url_encode(
            json.dumps(obj, separators=(",", ":")).encode()
        )

    @classmethod
    def decode_json(cls, data: bytes) -> dict:
        return json.loads(CMNUtils.b64url_decode(data).decode())
    
class CMNUtils:
    @staticmethod
    def b64url_encode(data: bytes) -> bytes:
        return base64.urlsafe_b64encode(data).rstrip(b'=')

    @staticmethod
    def b64url_decode(data: bytes) -> bytes:
        return base64.urlsafe_b64decode(data + b'=' * (-len(data) % 4))

    @staticmethod
    def to_bytes(data: str | bytes | bytearray | memoryview) -> bytes:
        if isinstance(data, bytes):
            return data
        elif isinstance(data, str):
            return data.encode("utf-8")
        elif isinstance(data, (bytearray, memoryview)):
            return bytes(data)
        else:
            raise TypeError(f"Expected str, bytes, bytearray, or memoryview, got {type(data)}")
        
    @staticmethod
    def to_str(data: str | bytes | bytearray | memoryview) -> str:
        if isinstance(data, str):
            return data
        elif isinstance(data, (bytes, bytearray, memoryview)):
            return bytes(data).decode("utf-8")
        else:
            raise TypeError(f"Expected str, bytes, bytearray, or memoryview, got {type(data)}")
    
    @staticmethod
    def is_rsa_key(key):
        return isinstance(key, (rsa.RSAPublicKey, rsa.RSAPrivateKey))

    @staticmethod
    def is_ec_key(key):
        return isinstance(key, (ec.EllipticCurvePublicKey, ec.EllipticCurvePrivateKey))