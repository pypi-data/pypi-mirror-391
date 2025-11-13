"""
Metadata encryption support for Snakemake persistence layer.

This module provides optional encryption of sensitive metadata fields
to protect business logic and proprietary workflows.
"""

__author__ = "Johannes Köster"
__copyright__ = "Copyright 2022, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

import json
from typing import Any, Optional


class MetadataEncryptor:
    """
    Encrypts and decrypts sensitive fields in metadata records.

    When enabled, this encrypts the following sensitive fields:
    - code: Rule source code
    - shellcmd: Shell command strings
    - params: Parameter values

    This protects proprietary algorithms and business logic from being
    visible even if the .snakemake directory is accessed.
    """

    def __init__(self, encryption_key: Optional[bytes] = None):
        """
        Initialize the encryptor.

        Args:
            encryption_key: Fernet encryption key (32 bytes, base64 encoded).
                          If None, encryption is disabled.
        """
        self.enabled = encryption_key is not None

        if self.enabled:
            try:
                from cryptography.fernet import Fernet
            except ImportError:
                raise ImportError(
                    "Metadata encryption requires the 'cryptography' package. "
                    "Install it with: pip install cryptography"
                )

            self.cipher = Fernet(encryption_key)
            self.sensitive_fields = ["code", "shellcmd", "params"]
        else:
            self.cipher = None
            self.sensitive_fields = []

    def encrypt_record(self, record: dict) -> dict:
        """
        Encrypt sensitive fields in a metadata record.

        Args:
            record: The metadata record dictionary

        Returns:
            Record with sensitive fields encrypted
        """
        if not self.enabled:
            return record

        encrypted = record.copy()

        for field in self.sensitive_fields:
            if field in encrypted and encrypted[field]:
                # Serialize the field value
                value_str = json.dumps(encrypted[field], ensure_ascii=False)

                # Encrypt
                encrypted_value = self.cipher.encrypt(value_str.encode()).decode()

                # Mark as encrypted
                encrypted[field] = {
                    "_encrypted": True,
                    "_value": encrypted_value,
                }

        return encrypted

    def decrypt_record(self, record: dict) -> dict:
        """
        Decrypt encrypted fields in a metadata record.

        Args:
            record: The metadata record dictionary

        Returns:
            Record with encrypted fields decrypted
        """
        if not self.enabled:
            return record

        decrypted = record.copy()

        for field in self.sensitive_fields:
            if field in decrypted and isinstance(decrypted[field], dict):
                if decrypted[field].get("_encrypted"):
                    try:
                        # Decrypt the value
                        encrypted_value = decrypted[field]["_value"]
                        decrypted_bytes = self.cipher.decrypt(encrypted_value.encode())
                        value_str = decrypted_bytes.decode()

                        # Deserialize
                        decrypted[field] = json.loads(value_str)

                    except Exception as e:
                        # If decryption fails, keep the encrypted value
                        # This handles cases where the wrong key is used
                        from snakemake.logging import logger

                        logger.warning(
                            f"Failed to decrypt metadata field '{field}': {e}. "
                            "This may indicate an incorrect encryption key."
                        )

        return decrypted


def create_encryptor(encryption_key: Optional[bytes] = None) -> MetadataEncryptor:
    """
    Factory function to create a MetadataEncryptor.

    Args:
        encryption_key: Optional encryption key. If None, encryption is disabled.

    Returns:
        MetadataEncryptor instance
    """
    return MetadataEncryptor(encryption_key)
