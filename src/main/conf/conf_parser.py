import os

import toml
from dotenv import load_dotenv

from src.main.conf.conf_classes import AppConfig, Target, ScannerConfig, SMTPConfig, DigitalOcean
from src.utils.logger import ConsoleLogger
from src.utils.singleton import Singleton


class ConfigLoader(metaclass=Singleton):
    @staticmethod
    def load_config(file_path: str = "config.toml", with_env: bool = False) -> AppConfig:
        if with_env:
            load_dotenv()
        config_data = toml.load(file_path)
        ConsoleLogger().info("Loaded config.toml")
        smtp_config = SMTPConfig(
            smtp_server=os.getenv('smtp_server'),
            smtp_port=os.getenv('smtp_port'),
            smtp_username=os.getenv('smtp_username'),
            smtp_password=os.getenv('smtp_password'),
            sender=os.getenv('sender'),
            recipients=os.getenv('recipients'),
        )
        if "," in smtp_config.recipients:
            smtp_config.recipients = smtp_config.recipients.split(",")
        if type(smtp_config.smtp_port) == str:
            smtp_config.smtp_port = int(smtp_config.smtp_port)
        ConsoleLogger().info("Loaded SMTPConfig")
        scanner = [
            ScannerConfig(
                scan_interval=scanner['scan_interval'],
                scan_start=scanner['scan_start'],
                scan_end=scanner['scan_end'],
                scanner_id=scanner['scanner_id'],
            )
            for scanner in config_data['app']['scanner']
        ]
        ConsoleLogger().info("Loaded Scanners")

        targets = [
            Target(
                target_id=target['target_id'],
                message_subject=target['message_subject'],
                message_body=target['message_body'],
                target_url=target['target_url'],
                target_string=target['target_string'],
                alert_when_found=target.get('alert_when_found', None),
                alert_when_not_found=target.get('alert_when_not_found', None),
                scanner_id=target['scanner_id'],
            )
            for target in config_data['app']['targets']
        ]
        ConsoleLogger().info("Loaded targets")
        digital_ocean = DigitalOcean(api_key=os.getenv('do_api_key'))
        ConsoleLogger().info("Loaded DO key")
        ConsoleLogger().info("Will return AppConfig object")

        return AppConfig(smtp=smtp_config, scanners=scanner, targets=targets, digital_ocean=digital_ocean)
