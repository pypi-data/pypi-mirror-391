"""
Doc String
"""
import base64
import secrets
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

__all__ = ["AES"]

class AES:
    # Constants
    PASSWORD_SIZE = 48
    SALT_SIZE = 18
    SHARED_KEY_SIZE = PASSWORD_SIZE + SALT_SIZE
    KEY_SIZE = 32
    NONCE_SIZE = 16
    TAG_LENGTH = 16
    PBKDF2_ITERATIONS = 100_000
    LABEL = b"secure_token"
    RSA_HASH = {
        4096: hashes.SHA512(),
        3072: hashes.SHA384(),
        2048: hashes.SHA256()
    }

    @classmethod
    def cekey(cls, input_bytes: bytes | None = None):
        input_bytes = input_bytes or secrets.token_bytes(cls.SHARED_KEY_SIZE)
        return cls.derive_from_input(input_bytes)

    @classmethod
    def derive_from_input(cls, input_bytes: bytes):
        required_length = cls.PASSWORD_SIZE + cls.SALT_SIZE
        if len(input_bytes) < required_length:
            raise ValueError(f"Input must be at least {required_length} bytes (got {len(input_bytes)} bytes)")

        password = input_bytes[:cls.PASSWORD_SIZE]
        salt = input_bytes[-cls.SALT_SIZE:]
        return cls.derive_key_nonce(password, salt)

    @classmethod
    def cekenc(cls, plain_cek: str, public_key: rsa.RSAPublicKey) -> str:
        hash_algo = cls.select_hash(public_key)
        cek_bytes = plain_cek.encode("utf-8")
        cipher_bytes = public_key.encrypt(
            cek_bytes,
            padding.OAEP(
                mgf=padding.MGF1(hash_algo),
                algorithm=hash_algo,
                label=cls.LABEL,
            ),
        )
        return base64.urlsafe_b64encode(cipher_bytes).decode("utf-8")

    @classmethod
    def cekdec(cls, urlsafe_ciphercek: str, private_key: rsa.RSAPrivateKey) -> str:
        hash_algo = cls.select_hash(private_key)
        cipher_bytes = base64.urlsafe_b64decode(urlsafe_ciphercek.encode("utf-8"))
        cek_bytes = private_key.decrypt(
            cipher_bytes,
            padding.OAEP(
                mgf=padding.MGF1(hash_algo),
                algorithm=hash_algo,
                label=cls.LABEL,
            ),
        )
        return cek_bytes.decode("utf-8")
    
    @classmethod
    def select_hash(cls, key) -> hashes.HashAlgorithm:
        if isinstance(key, (rsa.RSAPrivateKey, rsa.RSAPublicKey)):
            size = key.key_size
            return (
                cls.RSA_HASH.get(size)
                or hashes.SHA256()
            )
        raise ValueError("Unsupported key type for hash selection")

    @staticmethod
    def sharedkey(private_key: ec.EllipticCurvePrivateKey, peer_public_key: ec.EllipticCurvePublicKey) -> bytes:
        return private_key.exchange(ec.ECDH(), peer_public_key)

    @staticmethod
    def encrypt(plaintext: bytes, key: bytes, nonce: bytes, aad_bytes: bytes | None = None) -> bytes:
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce, min_tag_length=AES.TAG_LENGTH),
            backend=default_backend(),
        )
        encryptor = cipher.encryptor()
        if aad_bytes:
            encryptor.authenticate_additional_data(aad_bytes)
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        return ciphertext + encryptor.tag

    @staticmethod
    def decrypt(ciphertext_with_tag: bytes, key: bytes, nonce: bytes, aad_bytes: bytes | None = None) -> bytes:
        tag = ciphertext_with_tag[-AES.TAG_LENGTH:]
        ciphertext = ciphertext_with_tag[:-AES.TAG_LENGTH]
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce, tag),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()
        if aad_bytes:
            decryptor.authenticate_additional_data(aad_bytes)
        return decryptor.update(ciphertext) + decryptor.finalize()

    @staticmethod
    def derive_key_nonce(password: bytes, salt: bytes) -> tuple[bytes, bytes]:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=AES.KEY_SIZE + AES.NONCE_SIZE,
            salt=salt,
            iterations=AES.PBKDF2_ITERATIONS,
            backend=default_backend(),
        )
        key_nonce = kdf.derive(password)
        return key_nonce[:AES.KEY_SIZE], key_nonce[-AES.NONCE_SIZE:]
        
    