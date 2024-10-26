import sys
from threading import Thread

from src.main.conf.conf_classes import ScannerConfig
from src.main.conf.conf_parser import ConfigLoader
from src.main.events.result import EventResult
from src.main.scanning.scanner import Scanner
from src.main.scraping.scraper import Scraper


class Executor:
    @staticmethod
    def run_scraper() -> None:
        try:
            scanners = ConfigLoader().load_config().scanners
            targets = ConfigLoader().load_config().targets
            for target in targets:
                scanner = ScannerConfig.get_scanner_by_id(scanners, target.scanner_id)
                event_result = EventResult()
                Thread(target=Scanner().run_scanner, args=[scanner, (Scraper.scrape_target, target, event_result)]).start()
        except KeyboardInterrupt:
            sys.exit(0)
