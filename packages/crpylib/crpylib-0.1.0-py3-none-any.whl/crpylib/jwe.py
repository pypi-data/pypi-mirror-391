"""
Doc String

"""
import zlib
import json
import base64
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from .aes import AES
from .sgn import SGN
from .key import KEY

__all__ = ["JWE"]


class JWE:
    CURVE_ALG = {
        "secp256r1": "ES256",
        "secp384r1": "ES384",
        "secp521r1": "ES512",
        "secp256k1": "ES256K"
    }
    @classmethod
    def encode(cls, payload, peer_key, key=None, cty=None, kid=None, sign=False):
        alg = cls.jwealg(peer_key)
        header = JWEHeader(alg=alg, enc="A256GCM", zip="DEF", cty=cty, kid=kid).encode()

        if CMNUtils.is_rsa_key(peer_key):
            if key is not None and CMNUtils.is_ec_key(key):
                aes_key, iv, cek = cls.rsacek(peer_key, key)
            else:
                aes_key, iv, cek = cls.rsacek(peer_key)
        elif CMNUtils.is_ec_key(peer_key) and CMNUtils.is_ec_key(key):
            aes_key, iv, cek = cls.ecccek(peer_key, key)
        else:
            raise ValueError(f"Unsupported key types: {type(peer_key)}, {type(key)}")

        compressed = JWEUtils.compress(CMNUtils.to_bytes(payload), method="DEF")
        ciphertext_with_tag = AES.encrypt(compressed, aes_key, iv, header)

        ciphertext, tag = ciphertext_with_tag[:-16], ciphertext_with_tag[-16:]
        parts = [
            header,
            cek,
            CMNUtils.b64url_encode(iv),
            CMNUtils.b64url_encode(ciphertext),
            CMNUtils.b64url_encode(tag)
        ]
        jwe = JWEUtils.serialize(*parts)
        return cls.sign(jwe, key) if sign and key is not None else CMNUtils.to_str(jwe)

    @classmethod
    def decode(cls, jwe_string, key):
        header, cek, iv_b64, ct_b64, tag_b64, signed = JWEUtils.deserialize(CMNUtils.to_bytes(jwe_string))
        header_dict = JWEHeader.decode(header)
        alg = header_dict["alg"]
        if alg.startswith("RS") and CMNUtils.is_rsa_key(key):
            aes_key, iv, peer_key = cls.rsapek(cek, key)
            if signed and peer_key is not None:
                cls.verify(jwe_string, peer_key)
        elif alg.startswith("ES") and CMNUtils.is_ec_key(key):
            aes_key, iv, peer_key = cls.eccpek(cek, key)
            if signed:
                cls.verify(jwe_string, peer_key)
        else:
            raise ValueError(f"Unsupported algorithm or key type: {alg}, {type(key)}")

        if CMNUtils.b64url_decode(iv_b64) != iv:
            raise ValueError("IV mismatch — possible tampering or unsupported JWE")

        ciphertext = CMNUtils.b64url_decode(ct_b64)
        tag = CMNUtils.b64url_decode(tag_b64)
        zipped = AES.decrypt(ciphertext + tag, aes_key, iv, header)
        return CMNUtils.to_str(JWEUtils.decompress(zipped, header_dict.get("zip", "DEF")))
    
    @classmethod
    def jwealg(cls, key):
        if CMNUtils.is_rsa_key(key):
            size = key.key_size
            return f"RS{512 if size >= 4096 else 384 if size >= 3072 else 256}"
        elif CMNUtils.is_ec_key(key):
            return cls.CURVE_ALG.get(key.curve.name, "ES256")
        else:
            raise ValueError("Unsupported key type")

    @staticmethod
    def sign(jwe_bytes, private_key):
        jwe_bytes = CMNUtils.to_bytes(jwe_bytes)
        signing_input = jwe_bytes.split(b".", 1)[0]
        signature = SGN.sign(private_key, signing_input)
        return CMNUtils.to_str(jwe_bytes + b"." + CMNUtils.to_bytes(signature))

    @staticmethod
    def verify(signed_jwe, public_key):
        signed_jwe = CMNUtils.to_bytes(signed_jwe)
        signing_input = signed_jwe.split(b".", 1)[0]
        signature = signed_jwe.rsplit(b".", 1)[1]
        SGN.verify(public_key, signature, signing_input)

    @staticmethod
    def rsacek(peer_key, key=None):
        if key is not None:
            jwk = KEY(key.public_key()).to_jwk()
            jwk_dict = json.loads(jwk)
            input_bytes = CMNUtils.to_bytes(jwk_dict['x'] + jwk_dict['y'])
            jwk_dict['x'] = AES.cekenc(jwk_dict['x'], peer_key)
            jwk_dict['y'] = AES.cekenc(jwk_dict['y'], peer_key)
            encrypted_str = json.dumps(jwk_dict)
        else:
            jwk_dict = {}
            input_str = next(KEY.SYM.urlsafe().keygen)
            input_bytes = CMNUtils.to_bytes(input_str)
            jwk_dict['k'] = AES.cekenc(input_str, peer_key)
            encrypted_str = json.dumps(jwk_dict)
        cek = CMNUtils.b64url_encode(CMNUtils.to_bytes(encrypted_str))
        aes_key, iv = JWEUtils.aes_key_iv(CMNUtils.to_bytes(input_bytes))
        return aes_key, iv, cek
    
    @staticmethod
    def ecccek(peer_key, key):
        jwk = KEY(key.public_key()).to_jwk()
        cek = CMNUtils.b64url_encode(CMNUtils.to_bytes(jwk))
        shared_key = JWEUtils.shared_key(key, peer_key)
        aes_key, iv = JWEUtils.aes_key_iv(shared_key)
        return aes_key, iv, cek
    
    @staticmethod
    def rsapek(cek: bytes, key):
        json_str = CMNUtils.to_str(CMNUtils.b64url_decode(cek))
        json_obj = json.loads(json_str)
        if json_obj.get("k") is not None :
            input_str = json_obj["k"]
            decrypted_str = AES.cekdec(input_str, key)
            input_bytes = CMNUtils.to_bytes(decrypted_str)
            peer_key = None
        else:
            jwk_dict = json_obj
            jwk_dict['x'] = AES.cekdec(jwk_dict['x'], key)
            jwk_dict['y'] = AES.cekdec(jwk_dict['y'], key)
            input_bytes = CMNUtils.to_bytes(jwk_dict['x'] + jwk_dict['y'])
            peer_key = KEY.from_jwk(json.dumps(jwk_dict)).public
        aes_key, iv = JWEUtils.aes_key_iv(input_bytes)
        return aes_key, iv, peer_key
    
    @staticmethod
    def eccpek(cek: bytes, key):
        jwk_json = CMNUtils.to_str(CMNUtils.b64url_decode(cek))
        peer_key = KEY.from_jwk(jwk_json).public
        shared_key = AES.sharedkey(key, peer_key)
        aes_key, iv = JWEUtils.aes_key_iv(shared_key)
        return aes_key, iv, peer_key

  
class JWEHeader:
    def __init__(self, alg, enc, zip, cty=None, kid=None):
        self.header = {"alg": alg, "enc": enc, "zip": zip}
        if cty: self.header["cty"] = cty
        if kid: self.header["kid"] = kid

    def encode(self) -> bytes:
        json_header = json.dumps(self.header, separators=(",", ":"), sort_keys=True).encode()
        return CMNUtils.b64url_encode(json_header)

    @staticmethod
    def decode(encoded_header: bytes) -> dict:
        return json.loads(CMNUtils.b64url_decode(encoded_header))

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
    
class JWEUtils:
    @staticmethod
    def compress(data: bytes, method="DEF") -> bytes:
        return zlib.compress(data) if method == "DEF" else data

    @staticmethod
    def decompress(data: bytes, method="DEF") -> bytes:
        return zlib.decompress(data) if method == "DEF" else data

    @staticmethod
    def serialize(header, cek, iv, ciphertext, tag) -> bytes:
        return b".".join(map(CMNUtils.to_bytes, [header, cek, iv, ciphertext, tag]))

    @staticmethod
    def deserialize(jwe_bytes: bytes):
        parts = jwe_bytes.split(b".")
        if len(parts) == 6:
            return *parts[:5], True
        elif len(parts) == 5:
            return *parts, False
        else:
            raise ValueError("Invalid JWE format")

    @staticmethod
    def aes_key_iv(input_bytes=None):
        return AES.cekey(input_bytes)

    @staticmethod
    def shared_key(private_key, peer_key):
        return AES.sharedkey(private_key, peer_key)