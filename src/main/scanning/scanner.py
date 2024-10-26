import time
from datetime import timedelta, datetime
from typing import Tuple, Any, Callable

from src.conf.conf_classes import ScannerConfig, Target
from src.main.events.result import EventResult
from src.main.utils.logger import ConsoleLogger


class Scanner:
    @staticmethod
    def parse_time_interval(interval_str: str) -> timedelta:
        """Parse a time interval string into a timedelta object."""
        days, hours, minutes, seconds = map(int, interval_str.split(':'))
        return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    @staticmethod
    def parse_time(time_str: str) -> time:
        """Parse a time string into a datetime object for today."""
        return datetime.strptime(time_str, '%H:%M:%S').time()

    @staticmethod
    def should_scan(current_time: time, scan_start: time, scan_end: time):
        """Check if the current time is within the scanning time range."""
        return scan_start <= current_time <= scan_end

    def run_scanner(self, scanner: ScannerConfig,
                    func_n_args: Tuple[Callable[[Target, EventResult], None], Target,EventResult]):
        """Run the scanner based on the configuration."""
        logger = ConsoleLogger()
        func, args,event = func_n_args
        scan_interval = self.parse_time_interval(scanner.scan_interval)
        scan_start = self.parse_time(scanner.scan_start)
        scan_end = self.parse_time(scanner.scan_end)

        while True:
            current_time = datetime.now().time()

            if self.should_scan(current_time, scan_start, scan_end):
                logger.info(f'[{args.target_id}] Scan started: {time.strftime("%H:%M:%S")}')
                func(args, event)
                logger.info(f'[{args.target_id}] Scan ended: {time.strftime("%H:%M:%S")}')
                logger.info(f"[{args.target_id}] Going to sleep for: {scan_interval}")
                time.sleep(scan_interval.total_seconds())
            else:
                # If outside of scan hours, sleep for a while before checking again
                logger.info(f'[{args.target_id}] Scanning time is between {scan_start} and {scan_end}')
                logger.info(f"[{args.target_id}] Going to sleep for 60 seconds.")
                time.sleep(60)
