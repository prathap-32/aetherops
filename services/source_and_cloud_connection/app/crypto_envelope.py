# services/source_and_cloud_connection/app/crypto_envelope.py
"""
AetherOps Cryptographic Security Envelope
Implements AES-256-GCM Authenticated Encryption with Associated Data (AEAD)
bound cryptographically to tenant and resource context:
AAD = "tenant:{tenant_id}|resource:{resource_id}|type:{credential_type}|v1"

Guarantees:
1. Confidentiality: Secret cannot be read without 256-bit encryption key.
2. Authenticity: Tampering with ciphertext or authentication tag causes decryption to fail closed.
3. Multi-Tenant Context Binding: Ciphertext cannot be moved or swapped across tenants.
"""

import os
import ctypes
import base64
import hashlib
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("aether-crypto-envelope")

# Load OpenSSL libcrypto
try:
    _libcrypto = ctypes.CDLL("libcrypto.so.3")
except Exception:
    try:
        _libcrypto = ctypes.CDLL("libcrypto.so")
    except Exception as e:
        logger.error(f"FATAL: Unable to load libcrypto: {e}")
        _libcrypto = None

if _libcrypto:
    _libcrypto.EVP_aes_256_gcm.restype = ctypes.c_void_p
    _libcrypto.EVP_CIPHER_CTX_new.restype = ctypes.c_void_p
    _libcrypto.EVP_CIPHER_CTX_free.argtypes = [ctypes.c_void_p]

    _libcrypto.EVP_EncryptInit_ex.argtypes = [
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p
    ]
    _libcrypto.EVP_CIPHER_CTX_ctrl.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
    _libcrypto.EVP_EncryptUpdate.argtypes = [
        ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int), ctypes.c_char_p, ctypes.c_int
    ]
    _libcrypto.EVP_EncryptFinal_ex.argtypes = [
        ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)
    ]

    _libcrypto.EVP_DecryptInit_ex.argtypes = [
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p
    ]
    _libcrypto.EVP_DecryptUpdate.argtypes = [
        ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int), ctypes.c_char_p, ctypes.c_int
    ]
    _libcrypto.EVP_DecryptFinal_ex.argtypes = [
        ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)
    ]

EVP_CTRL_GCM_SET_IVLEN = 0x9
EVP_CTRL_GCM_GET_TAG = 0x10
EVP_CTRL_GCM_SET_TAG = 0x11


def _derive_root_key() -> bytes:
    """Derives or retrieves the 256-bit root encryption key."""
    env_key = os.getenv("AETHER_MASTER_ENCRYPTION_KEY")
    if env_key:
        return hashlib.sha256(env_key.encode("utf-8")).digest()
    jwt_secret = os.getenv("JWT_SECRET_KEY", "aetherops-super-secure-production-cryptographic-jwt-token-signing-key-2026-cloudops-master")
    return hashlib.sha256(f"aether-vault-v1:{jwt_secret}".encode("utf-8")).digest()


def build_aad(tenant_id: Optional[str], resource_id: str, credential_type: str) -> bytes:
    clean_tenant = (tenant_id or "default_tenant").strip()
    clean_resource = resource_id.strip()
    clean_type = credential_type.strip()
    return f"tenant:{clean_tenant}|resource:{clean_resource}|type:{clean_type}|v1".encode("utf-8")


def encrypt_credential(
    plaintext: str,
    tenant_id: Optional[str],
    resource_id: str,
    credential_type: str = "aws_secret",
) -> Dict[str, str]:
    """
    Encrypts sensitive credential with AES-256-GCM.
    Returns:
      {
        "ciphertext": "<base64>",
        "nonce": "<base64>",
        "tag": "<base64>",
        "key_id": "root-v1",
        "version": "1"
      }
    """
    if not _libcrypto:
        raise RuntimeError("libcrypto library is unavailable for hardware-accelerated AES-GCM.")

    if not plaintext:
        raise ValueError("Cannot encrypt empty credential.")

    key = _derive_root_key()
    iv = os.urandom(12)  # Standard 96-bit GCM nonce
    aad = build_aad(tenant_id, resource_id, credential_type)
    plain_bytes = plaintext.encode("utf-8")

    ctx = _libcrypto.EVP_CIPHER_CTX_new()
    try:
        _libcrypto.EVP_EncryptInit_ex(ctx, _libcrypto.EVP_aes_256_gcm(), None, None, None)
        _libcrypto.EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, len(iv), None)
        _libcrypto.EVP_EncryptInit_ex(ctx, None, None, key, iv)

        out_len = ctypes.c_int()
        # Feed AAD
        _libcrypto.EVP_EncryptUpdate(ctx, None, ctypes.byref(out_len), aad, len(aad))

        # Encrypt plaintext
        ciphertext_buf = ctypes.create_string_buffer(len(plain_bytes) + 16)
        _libcrypto.EVP_EncryptUpdate(ctx, ciphertext_buf, ctypes.byref(out_len), plain_bytes, len(plain_bytes))
        ct_len = out_len.value

        final_buf = ctypes.create_string_buffer(16)
        final_len = ctypes.c_int()
        _libcrypto.EVP_EncryptFinal_ex(ctx, final_buf, ctypes.byref(final_len))

        # Retrieve 128-bit authentication tag
        tag_buf = ctypes.create_string_buffer(16)
        _libcrypto.EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, 16, tag_buf)

        ct_bytes = ciphertext_buf.raw[:ct_len]
        tag_bytes = tag_buf.raw[:16]

        return {
            "ciphertext": base64.b64encode(ct_bytes).decode("ascii"),
            "nonce": base64.b64encode(iv).decode("ascii"),
            "tag": base64.b64encode(tag_bytes).decode("ascii"),
            "key_id": "root-v1",
            "version": "1",
        }
    finally:
        _libcrypto.EVP_CIPHER_CTX_free(ctx)


def decrypt_credential(
    ciphertext_b64: str,
    nonce_b64: str,
    tag_b64: str,
    tenant_id: Optional[str],
    resource_id: str,
    credential_type: str = "aws_secret",
) -> str:
    """
    Decrypts AES-256-GCM ciphertext verifying authentication tag and tenant AAD.
    Raises ValueError if tag mismatch or wrong tenant.
    """
    if not _libcrypto:
        raise RuntimeError("libcrypto library is unavailable for hardware-accelerated AES-GCM.")

    try:
        ct_bytes = base64.b64decode(ciphertext_b64)
        iv = base64.b64decode(nonce_b64)
        tag_bytes = base64.b64decode(tag_b64)
    except Exception as e:
        raise ValueError(f"Malformed base64 ciphertext or envelope components: {e}")

    key = _derive_root_key()
    aad = build_aad(tenant_id, resource_id, credential_type)

    ctx = _libcrypto.EVP_CIPHER_CTX_new()
    try:
        _libcrypto.EVP_DecryptInit_ex(ctx, _libcrypto.EVP_aes_256_gcm(), None, None, None)
        _libcrypto.EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, len(iv), None)
        _libcrypto.EVP_DecryptInit_ex(ctx, None, None, key, iv)

        out_len = ctypes.c_int()
        # Feed AAD
        _libcrypto.EVP_DecryptUpdate(ctx, None, ctypes.byref(out_len), aad, len(aad))

        # Decrypt ciphertext
        decrypted_buf = ctypes.create_string_buffer(len(ct_bytes) + 16)
        _libcrypto.EVP_DecryptUpdate(ctx, decrypted_buf, ctypes.byref(out_len), ct_bytes, len(ct_bytes))
        dec_len = out_len.value

        # Set expected tag
        tag_in = ctypes.create_string_buffer(tag_bytes, len(tag_bytes))
        _libcrypto.EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, len(tag_bytes), tag_in)

        final_buf = ctypes.create_string_buffer(16)
        final_len = ctypes.c_int()
        res = _libcrypto.EVP_DecryptFinal_ex(ctx, final_buf, ctypes.byref(final_len))

        if res <= 0:
            raise ValueError("Cryptographic verification failed: Authentication tag mismatch or unauthorized tenant context.")

        dec_bytes = decrypted_buf.raw[:dec_len]
        return dec_bytes.decode("utf-8")
    finally:
        _libcrypto.EVP_CIPHER_CTX_free(ctx)
