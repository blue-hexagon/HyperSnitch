import sys
from threading import Thread
from typing import List

from src.main.conf.conf_classes import ScannerConfig
from src.main.conf.conf_parser import ConfigLoader
from src.main.events.result import EventResult
from src.main.scanning.scanner import Scanner
from src.main.scraping.scraper import Scraper
from src.utils.logger import ConsoleLogger


class Executor:
    @staticmethod
    def deploy_threads() -> List[Thread]:
        logger = ConsoleLogger().logger
        threads: List[Thread] = []
        scanners = ConfigLoader().load_config().scanners
        targets = ConfigLoader().load_config().targets
        for target in targets:
            scanner = ScannerConfig.get_scanner_by_id(scanners, target.scanner_id)
            event_result = EventResult()
            logger.info(f"Creating (but not starting) new thread for {target.target_id}")
            threads.append(Thread(target=Scanner().run_scanner, args=[scanner, (Scraper.scrape_target, target, event_result)]))
        return threads

    @staticmethod
    def start_threads(threads: List[Thread]) -> None:
        ConsoleLogger().info("Starting threads")
        for thread in threads:
            thread.start()

    @staticmethod
    def run():
        threads = Executor.deploy_threads()
        ConsoleLogger().info("Retrieved threads")
        Executor.start_threads(threads)
