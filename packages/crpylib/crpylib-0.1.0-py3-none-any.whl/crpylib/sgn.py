import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, ec

class SGN:
    RSA_HASH = {
        4096: hashes.SHA512(),
        3072: hashes.SHA384(),
        2048: hashes.SHA256()
    }

    EC_HASH = {
        "secp256r1": hashes.SHA256(),
        "secp384r1": hashes.SHA384(),
        "secp521r1": hashes.SHA512(),
        "secp256k1": hashes.SHA256()
    }
    @classmethod
    def sign(
        cls,
        private_key, 
        signing_input: str | bytes
        ) -> str:
        data = CMNUtils.to_bytes(signing_input)
        hash_algo = cls.select_hash(private_key)

        if CMNUtils.is_rsa_key(private_key):
            signature = private_key.sign(
                data,
                padding.PSS(
                    mgf=padding.MGF1(hash_algo),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hash_algo
            )
        elif CMNUtils.is_ec_key(private_key):
            signature = private_key.sign(data, ec.ECDSA(hash_algo))
        else:
            raise ValueError(f"Unsupported key type for signing: {type(private_key)}")

        return CMNUtils.to_str(CMNUtils.b64url_encode(signature))

    @classmethod
    def verify(
        cls,
            public_key, 
            signature_b64: str | bytes, 
            signing_input: str | bytes
        ) -> None:
        data = CMNUtils.to_bytes(signing_input)
        signature = CMNUtils.b64url_decode(CMNUtils.to_bytes(signature_b64))
        hash_algo = cls.select_hash(public_key)

        try:
            if CMNUtils.is_rsa_key(public_key):
                public_key.verify(
                    signature,
                    data,
                    padding.PSS(
                        mgf=padding.MGF1(hash_algo),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hash_algo
                )
            elif CMNUtils.is_ec_key(public_key):
                public_key.verify(signature, data, ec.ECDSA(hash_algo))
            else:
                raise ValueError(f"Unsupported key type for verification: {type(public_key)}")
        except Exception as exc:
            raise ValueError(f"Signature verification failed for key type {type(public_key)}") from exc
    
    @classmethod
    def select_hash(cls, key) -> hashes.HashAlgorithm:
        if CMNUtils.is_rsa_key(key):
            size = key.key_size
            return (
                cls.RSA_HASH.get(size)
                or hashes.SHA256()
            )
        elif CMNUtils.is_ec_key(key):
            name = key.curve.name
            return cls.EC_HASH.get(name, hashes.SHA256())
        else:
            raise ValueError(f"Unsupported key type for hash selection: {type(key)}")
 
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
    def is_rsa_key(key) -> bool:
        return isinstance(key, (rsa.RSAPublicKey, rsa.RSAPrivateKey))

    @staticmethod
    def is_ec_key(key) -> bool:
        return isinstance(key, (ec.EllipticCurvePublicKey, ec.EllipticCurvePrivateKey))