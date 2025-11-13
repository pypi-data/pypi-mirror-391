"""
Doc String

"""

import json
import base64
import secrets
import hashlib
from enum import Enum
from pathlib import Path
from typing import Any
from dataclasses import dataclass
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec

class KeySize(Enum):
    KEY16 = 16
    KEY32 = 32
    KEY64 = 64
    KEY128 = 128
    KEY256 = 256

@dataclass
class SYM:
    keygen : Any
    keytyp : str
    length : int
    KeySize = KeySize
    def write(self, file_name, file_path):
        file_path = Path(file_path)
        key_type = self.keytyp
        file_path = file_path / f"{file_name}"

        header = f"-----BEGIN {key_type.upper()} KEYS-----\n"
        footer = f"-----END {key_type.upper()} KEYS-----"

        lines = [header]
        for i, key in enumerate(self.keygen, start=1):
            if key_type == "byte":
                encoded = base64.b64encode(key).decode("utf-8").rstrip("=\n")
            else:
                encoded = key
            lines.append(f"{key_type}-key-{i}  {encoded}\n")
        lines.append(footer)

        file_path.write_text("".join(lines), encoding="utf-8")
        return str(file_path)
    
    @classmethod
    def byte(cls, key_size=KeySize.KEY128, num_key=1):
        key_gen = (secrets.token_bytes(key_size.value) for _ in range(num_key))
        return cls(key_gen, "byte", num_key)
    
    @classmethod
    def hex(cls, key_size = KeySize.KEY128, num_key=1):
        key_gen = (secrets.token_hex(key_size.value) for _ in range(num_key))
        return cls(key_gen, "hex", num_key)

    @classmethod
    def urlsafe(cls, key_size = KeySize.KEY128, num_key=1):
        key_gen = (secrets.token_urlsafe(key_size.value) for _ in range(num_key))
        return cls(key_gen, "urlsafe", num_key)
    
    @classmethod
    def file(cls, file_path, file_name):
        def _padding(s):
            return s + "=" * (-len(s) % 4)

        file_path = Path(file_path) / file_name
        lines = file_path.read_text(encoding="utf-8").strip().splitlines()

        key_type = lines[0].split()[1].lower()
        keys_raw = [line.split()[1].strip() for line in lines[1:-1]]

        if key_type == "byte":
            key_gen = (
                base64.b64decode(_padding(k)) for k in keys_raw
            )
        else:
            key_gen = (k.encode("utf-8") for k in keys_raw)

        return cls(key_gen, key_type, len(keys_raw))

class PRM:
    class KeyUse(Enum):
        SIGN = "sig"
        CIPH = "enc"

    class KidSize(Enum):
        KID08 = 8
        KID16 = 16
        KID32 = 32
        KID64 = 64

    class RSKSize(Enum):
        RSA2048 = 2048
        RSA3072 = 3072
        RSA4096 = 4096

    class ECCurve(Enum):
        SECP256R1 = ec.SECP256R1
        SECP384R1 = ec.SECP384R1
        SECP521R1 = ec.SECP521R1
        SECP256K1 = ec.SECP256K1
    
class KEY:
    SYM = SYM
    PRM = PRM
    CURVE_MAP = {
        "P-256": ec.SECP256R1,
        "P-384": ec.SECP384R1,
        "P-521": ec.SECP521R1,
        "secp256k1": ec.SECP256K1
    }

    CURVE_ALG = {
        "secp256r1": ("P-256", "ES256"),
        "secp384r1": ("P-384", "ES384"),
        "secp521r1": ("P-521", "ES512"),
        "secp256k1": ("secp256k1", "ES256K")
    }


    def __init__(self, key, kid=None, use=None):
        self.key = key
        self.kid = kid
        self.use = use

    def __repr__(self):
        if hasattr(self.key, "private_bytes"):
            type = "private"
        elif hasattr(self.key, "private_bytes"):
            type = "public"
        else:
            type = "unknown"
        return f"Key(type='{type}', kid='{self.kid}', use= '{self.use}')"
    
    @property
    def public(self):
        if hasattr(self.key, "public_key"):
            return self.key.public_key()
        elif hasattr(self.key, "public_bytes"):
            return self.key  # Already a public key
        else:
            raise TypeError("Unsupported key type")
            
        
    def to_pem(
            self, 
            passphrase=None, 
            public=False
        ):
        key = self.public if public else self.key
        if hasattr(key, "private_bytes"):
            encryption = (
                serialization.BestAvailableEncryption(passphrase.encode("utf-8"))
                if passphrase else serialization.NoEncryption()
            )
            return key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption
            )
        else:
            return key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        
    def to_jwk(
            self, 
            public=False, 
            use = PRM.KeyUse.SIGN, 
            kid_size = PRM.KidSize.KID16
        ):
        if isinstance(self.public, rsa.RSAPublicKey):
            numbers = self.public.public_numbers()
            key_size = self.public.key_size
            alg = "RS512" if key_size >= 4096 else "RS384" if key_size >= 3072 else "RS256"

            jwk = {
                "kty": "RSA",
                "n": self.int_to_b64(numbers.n),
                "e": self.int_to_b64(numbers.e),
                "alg": alg
            }
            kid = self.kid or self.make_kid(jwk, kid_size.value)
            if not public and isinstance(self.key, rsa.RSAPrivateKey):
                priv = self.key.private_numbers()
                jwk.update({
                    "d": self.int_to_b64(priv.d),
                    "p": self.int_to_b64(priv.p),
                    "q": self.int_to_b64(priv.q),
                    "dp": self.int_to_b64(priv.dmp1),
                    "dq": self.int_to_b64(priv.dmq1),
                    "qi": self.int_to_b64(priv.iqmp)
                })

        elif isinstance(self.public, ec.EllipticCurvePublicKey):
            numbers = self.public.public_numbers()
            crv, alg = self.CURVE_ALG.get(self.public.curve.name, ("P-256", "ES256"))
            jwk = {
                "kty": "EC",
                "crv": crv,
                "x": self.int_to_b64(numbers.x),
                "y": self.int_to_b64(numbers.y),
                "alg": alg
            }
            kid = self.kid or self.make_kid(jwk, kid_size.value)
            # Add private field if requested and available
            if not public and isinstance(self.key, ec.EllipticCurvePrivateKey):
                priv = self.key.private_numbers()
                jwk["d"] = self.int_to_b64(priv.private_value)

        else:
            raise ValueError("Unsupported key type")
        
        jwk["kid"] = kid
        jwk["use"] = self.use or use.value
        return json.dumps(jwk, indent=2)
    
    def jwkset(self, _jwk_list = None):
        jwk = self.to_jwk(public=True)
        return {"keys": _jwk_list or [jwk]}
        
    def to_file(
            self, 
            key_name, 
            key_path, 
            passphrase=None, 
            public=False
        ):
        key = self.public if public else self.key
        key_path = Path(key_path)
        key_name = key_name if hasattr(key, "private_bytes") else f"{key_name}.pub"
        file_path = key_path / key_name
        pem_data = self.to_pem(passphrase, public)
        file_path.write_bytes(pem_data)
        return str(file_path)
    
    @classmethod
    def from_ecc(
            cls, 
            ec_curve=PRM.ECCurve.SECP521R1,
            kid=None,
            use = PRM.KeyUse.SIGN
        ):
        # Generate an ECC key pair
        curve = ec_curve.value
        key = ec.generate_private_key(
            curve(),
            backend=default_backend(),
        )
        return cls(key, kid, use.value)

    @classmethod
    def from_rsa(
            cls, 
            key_size=PRM.RSKSize.RSA4096,
            kid=None,
            use = PRM.KeyUse.SIGN
        ):
        key_size = key_size.value
        key = rsa.generate_private_key(
            public_exponent=65537, key_size=key_size, backend=default_backend()
        )
        return cls(key, kid, use.value)
    
    @classmethod
    def from_pem(
            cls, 
            pem_data, 
            passphrase=None,
            kid=None,
            use = PRM.KeyUse.SIGN
        ):
        try:
            passphrase = passphrase.encode("utf-8") if passphrase else None
            key = serialization.load_pem_private_key(pem_data, password=passphrase, backend=default_backend())
        except ValueError:
            key = serialization.load_pem_public_key(pem_data, backend=default_backend())
        return cls(key, kid, use.value)
    

    @classmethod
    def from_file(
            cls, 
            key_path, 
            file_name, 
            passphrase=None, 
            kid=None,
            use = PRM.KeyUse.SIGN, 
        ):
        key_path = Path(key_path)
        file_path = key_path / file_name
        key_data = file_path.read_bytes()
        return cls.from_pem(key_data, passphrase, kid, use)


    @classmethod
    def from_jwk(cls, jwk):
        jwk_dict = json.loads(jwk)
        kid = jwk_dict.get("kid")
        use = jwk_dict.get("use")
        if jwk_dict["kty"] == "RSA":
            pub = rsa.RSAPublicNumbers(
                e=cls.b64_to_int(jwk_dict["e"]),
                n=cls.b64_to_int(jwk_dict["n"])
            )
            if "d" in jwk_dict:
                priv = rsa.RSAPrivateNumbers(
                    p=cls.b64_to_int(jwk_dict["p"]),
                    q=cls.b64_to_int(jwk_dict["q"]),
                    d=cls.b64_to_int(jwk_dict["d"]),
                    dmp1=cls.b64_to_int(jwk_dict["dp"]),
                    dmq1=cls.b64_to_int(jwk_dict["dq"]),
                    iqmp=cls.b64_to_int(jwk_dict["qi"]),
                    public_numbers=pub
                )
                return cls(priv.private_key(), kid, use)
            else:
                return cls(pub.public_key(), kid, use)

        elif jwk_dict["kty"] == "EC":
            curve = cls.CURVE_MAP[jwk_dict["crv"]]
            pub = ec.EllipticCurvePublicNumbers(
                x=cls.b64_to_int(jwk_dict["x"]),
                y=cls.b64_to_int(jwk_dict["y"]),
                curve=curve()
            )
            if "d" in jwk_dict:
                priv = ec.EllipticCurvePrivateNumbers(
                    private_value=cls.b64_to_int(jwk_dict["d"]),
                    public_numbers=pub
                )
                return cls(priv.private_key(), kid, use)
            else:
                return cls(pub.public_key(), kid, use)

        else:
            raise ValueError("Unsupported key type")
        

    @staticmethod
    def b64_to_int(val):
        return int.from_bytes(base64.urlsafe_b64decode(val + '=' * (-len(val) % 4)), 'big')
    
    @staticmethod
    def int_to_b64(val):
        return base64.urlsafe_b64encode(val.to_bytes((val.bit_length() + 7) // 8, 'big')).rstrip(b'=').decode()
    
    @staticmethod
    def make_kid(jwk_dict, kid_size: int) -> str:
        thumbprint = hashlib.sha256(json.dumps(jwk_dict, sort_keys=True).encode()).digest()
        return  base64.urlsafe_b64encode(thumbprint[:kid_size]).rstrip(b"=").decode("utf-8")
    
    @staticmethod
    def shared(private_key, peer_key):
        return private_key.exchange(ec.ECDH(), peer_key)

