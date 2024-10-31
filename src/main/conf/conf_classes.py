from dataclasses import dataclass, field
from typing import List, Any


@dataclass
class DigitalOcean:
    api_key: str


@dataclass
class SMTPConfig:
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    sender: str
    recipients: str


@dataclass
class ScannerConfig:
    scan_interval: str
    scan_start: str
    scan_end: str
    scanner_id: str

    @staticmethod
    def get_scanner_by_id(scanners: List[Any], scanner_id: str) -> Any:
        for scanner in scanners:
            if scanner.scanner_id == scanner_id:
                return scanner


@dataclass
class Target:
    target_id: str
    message_subject: str
    message_body: str
    target_url: str
    target_string: str
    alert_when_found: bool
    alert_when_not_found: bool
    scanner_id: str


@dataclass
class AppConfig:
    smtp: SMTPConfig
    scanners: List[ScannerConfig] = field(default_factory=list)
    targets: List[Target] = field(default_factory=list)
    digital_ocean: DigitalOcean = field(default_factory=DigitalOcean)
