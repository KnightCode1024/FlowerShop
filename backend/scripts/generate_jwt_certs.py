import json
import uuid
import base64

from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend

OUT_DIR = Path("../certs")
OUT_DIR.mkdir(exist_ok=True)

PRIVATE_KEY_FILE = OUT_DIR / "jwt_private_key.pem"
PUBLIC_KEY_FILE = OUT_DIR / "jwt_public_key.pem"
PUBLIC_JWK_FILE = OUT_DIR / "jwt_public_jwk.json"
PUBLIC_JWKS_FILE = OUT_DIR / "jwt_public_jwks.json"

KEY_SIZE = 4096
PUBLIC_EXPONENT = 65537
KID = str(uuid.uuid4())


def ensure_outdir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def generate_rsa_key():
    return rsa.generate_private_key(
        public_exponent=PUBLIC_EXPONENT, key_size=KEY_SIZE, backend=default_backend()
    )


def write_private_key(path: Path, key):
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    path.write_bytes(pem)
    try:
        path.chmod(0o600)
    except PermissionError:
        pass


def write_public_key(path: Path, key):
    pub = key.public_key()
    pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    path.write_bytes(pem)


def int_to_base64url(n: int) -> str:
    length = (n.bit_length() + 7) // 8
    b = n.to_bytes(length, "big")
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def build_jwk_from_public_key(pubkey, kid: str, alg: str = "RS256", use: str = "sig"):
    numbers = pubkey.public_numbers()
    n_b64 = int_to_base64url(numbers.n)
    e_b64 = int_to_base64url(numbers.e)
    jwk = {"kty": "RSA", "use": use, "alg": alg, "kid": kid, "n": n_b64, "e": e_b64}
    return jwk


def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2))


def main():
    ensure_outdir(OUT_DIR)

    print("Generating RSA private key ({} bits)...".format(KEY_SIZE))
    key = generate_rsa_key()

    print("Writing private key to:", PRIVATE_KEY_FILE)
    write_private_key(PRIVATE_KEY_FILE, key)

    print("Writing public key to:", PUBLIC_KEY_FILE)
    write_public_key(PUBLIC_KEY_FILE, key)

    pubkey = key.public_key()
    jwk = build_jwk_from_public_key(pubkey, kid=KID)
    jwks = {"keys": [jwk]}

    print("Writing public JWK to:", PUBLIC_JWK_FILE)
    save_json(PUBLIC_JWK_FILE, jwk)

    print("Writing public JWKS to:", PUBLIC_JWKS_FILE)
    save_json(PUBLIC_JWKS_FILE, jwks)


if __name__ == "__main__":
    main()
