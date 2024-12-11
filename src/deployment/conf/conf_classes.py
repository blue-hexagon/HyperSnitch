from dataclasses import dataclass
from typing import List


@dataclass
class VPSConfig:
    vps_name: str
    api_slug: str
    image: str
    count: int
    tags: List[str]
    region: str


@dataclass
class SSHConfig:
    keyfile_name: str
    pubkey_remote_name: str
    passphrase: str
    key_bits: int


@dataclass
class FolderConfig:
    folder: str

@dataclass
class DomainConfig:
    domain_name: str
    subdomain: str
    ipv4: str

@dataclass
class DeployConfig:
    vps: VPSConfig
    ssh: SSHConfig
    folder: FolderConfig
    domain: DomainConfig

