import base64
import json
import os

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


class Crypto(object):

    def __init__(self, privkey: RSA.RsaKey):
        """
        Class constructor, use from_rsa_private_key() classmethod to instanciate

        Args:
            privkey (RSA.RsaKey): RSA imported private key
        """
        self.privkey = privkey

    @classmethod
    def from_rsa_private_key(cls, rsa_privkey: str):
        """
        Create a Crypto instance from RSA private key file.
        Note: RSA private key shall be the one used to generate API softsim key.

        Args:
            rsa_privkey (str): RSA private key file

        Raises:
            ValueError: If private key is not provided (i.e. None)

        Returns:
            Crypto: Class instance object
        """
        if rsa_privkey is None:
            raise ValueError("RSA private key not provided")

        private_key = RSA.import_key(rsa_privkey)
        return cls(private_key)

    @classmethod
    def from_rsa_private_file(cls, rsa_privkey_file: str):
        """
        Create a Crypto instance from RSA private key file.
        Note: RSA private key shall be the one used to generate API softsim key.

        Args:
            rsa_privkey (str): RSA private key file

        Raises:
            ValueError: If private key file is not provided (i.e. None)

        Returns:
            Crypto: Class instance object
        """
        if rsa_privkey_file is None:
            raise ValueError("RSA private file not provided")

        with open(rsa_privkey_file, "r", encoding="utf-8") as fd:
            data = fd.read()

        return cls.from_rsa_private_key(data)

    def _decrypt(self, iccid: str, profile_base64: str) -> dict:
        """
        Decrypt base64 encoded cipher profile

        Args:
            profile_base64 (str): Ciphered profile (base64 encoded)

        Returns:
            dict: Decrypted profile
        """
        profile = base64.b64decode(profile_base64)

        cipher_rsa = PKCS1_OAEP.new(self.privkey)
        profile = cipher_rsa.decrypt(profile)
        profile = json.loads(profile)
        profile.update({"iccid": iccid})

        return profile

    def next(self, profiles: dict) -> tuple[dict, dict]:
        """
        Pop and decrypt next profile from input dict (format as API-like json output)

        Args:
            profiles (dict): List of fetched profiles

        Returns:
            tuple[dict, dict]: Decrypted profile (ready to encode), Updated profiles list
        """
        encrypted = profiles["profiles"].pop(0)
        profile = self._decrypt(encrypted["iccid"], encrypted["profile"])
        count = profiles["count"] - 1
        profiles.update({"count": count})

        return profile, profiles if count > 0 else None
