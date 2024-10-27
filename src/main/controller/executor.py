import sys
from threading import Thread

from src.main.conf.conf_classes import ScannerConfig
from src.main.conf.conf_parser import ConfigLoader
from src.main.events.result import EventResult
from src.main.scanning.scanner import Scanner
from src.main.scraping.scraper import Scraper
from src.utils.logger import ConsoleLogger


class Executor:
    @staticmethod
    def run_scraper() -> None:
        logger = ConsoleLogger().logger
        try:
            scanners = ConfigLoader().load_config().scanners
            targets = ConfigLoader().load_config().targets
            logger.info("Loaded scanner and target configurations.")
            for target in targets:
                scanner = ScannerConfig.get_scanner_by_id(scanners, target.scanner_id)
                event_result = EventResult()
                logger.info(f"Deploying new thread for {target.target_id}")
                Thread(target=Scanner().run_scanner, args=[scanner, (Scraper.scrape_target, target, event_result)]).start()
        except KeyboardInterrupt:
            sys.exit(0)
