import os
from pathlib import Path

import paramiko

from src.conf.path_manager import PathManager
from src.main.utils.logger import ConsoleLogger


class SshUtils:
    logger = ConsoleLogger()

    def __init__(self, keyfile_name="id_rsa", passphrase=None):
        """
        Creates an SSH key-pair inside playbooks/profile folder with name `key_name`.pub for public, and
        `key_name` for private.

        Usage example:
        ssh_utils = SshUtils(profile_folder="test_profile", key_name="id_rsa", passphrase="Password1234!")
        ssh_utils.create_ssh_key_pair(key_bits=4096)
        print(ssh_utils.read_public_key())

        Passphrase is optional and can be omitted.
        """
        self.key_dir = os.path.expanduser(self.get_dir())
        self.key_name = keyfile_name
        self.passphrase = passphrase
        self.priv_key_path = Path(self.key_dir).joinpath(self.key_name)
        self.pub_key_path = self.priv_key_path.with_suffix(".pub")

    @staticmethod
    def get_dir():
        return PathManager().root / Path(".ssh")

    def create_ssh_key_pair(self, key_bits: int = 4096):
        os.makedirs(self.key_dir, exist_ok=True)

        key = paramiko.RSAKey.generate(bits=key_bits)
        private_key_path = self.create_private_key(key, self.key_dir, self.key_name, self.passphrase)
        public_key_path = self.create_public_key(key, self.key_dir, private_key_path)

        self.logger.info(f"SSH key pair created: Private key: {private_key_path}")
        self.logger.info(f"SSH key pair created: Public key: {public_key_path}")

        return private_key_path, public_key_path

    @classmethod
    def create_public_key(cls, key, key_dir, private_key_path):
        """Private key filepath is appended with .pub to create the pub key file"""
        public_key_path = os.path.join(key_dir, f"{private_key_path}.pub")
        public_key = f"{key.get_name()} {key.get_base64()}"
        with open(public_key_path, "w") as public_key_file:
            public_key_file.write(public_key)
        return public_key_path

    @classmethod
    def create_private_key(cls, key, key_dir, key_name, passphrase):
        private_key_path = os.path.join(key_dir, key_name)
        with open(private_key_path, "w") as private_key_file:
            key.write_private_key_file(private_key_file.name, password=passphrase)
        os.chmod(private_key_path, 0o600)
        return private_key_path

    def read_public_key(self):
        with open(self.pub_key_path, "r") as pub_key:
            return pub_key.readline()

    def read_private_key(self):
        with open(self.priv_key_path, "r") as priv_key:
            return priv_key.readline()
if __name__ == "__main__":
    sutils = SshUtils(keyfile_name="id_rsa")
    sutils.create_ssh_key_pair(key_bits=4096)
    print(sutils.read_public_key())
