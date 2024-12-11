from src.main.conf.conf_classes import Target
from src.main.conf.conf_parser import ConfigLoader
from src.main.events.result import EventResult
from src.main.notifier.smtp import send_email
from src.main.scraping.status import Status
from src.main.utils.domain import get_subdomain_domain_tld
from src.utils.logger import ConsoleLogger
from playwright.sync_api import sync_playwright


class Scraper:
    @staticmethod
    def search_string_on_website(url: str, search_string: str, target_id: str):
        logger = ConsoleLogger()
        logger.info("Entering scraper")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            logger.info(f"[{target_id}] Start searching for `{search_string}` on: {get_subdomain_domain_tld(url)}")
            page.goto(url)

            page.wait_for_load_state('networkidle')  # Wait for the page to load completely

            content = page.content()  # Get the page content

            if search_string in content:
                status = Status.FOUND
            else:
                status = Status.NOT_FOUND

            browser.close()
            return status

    @staticmethod
    def scrape_target(target: Target, event_result: EventResult) -> None:
        logger = ConsoleLogger()
        found_match: Status = (
            Scraper().search_string_on_website(
                target.target_url,
                target.target_string,
                target.target_id
            )
        )
        if target.alert_when_not_found and found_match == Status.NOT_FOUND:
            event_result.set_match()
            logger.info(f"[{target.target_id}] Scraping discovered that the string `{target.target_string}` is missing from website: {target.target_url}")
            if event_result.send_notification():
                logger.info(f"[{target.target_id}] Sending notification.")
                send_email(ConfigLoader().load_config().smtp, f"[!] {target.message_subject}", target.message_body)
        elif target.alert_when_found and found_match == Status.FOUND:
            event_result.set_match()
            logger.info(f"[{target.target_id}] Scraping discovered that the string `{target.target_string}` was found on the website: {target.target_url}")
            if event_result.send_notification():
                logger.info(f"[{target.target_id}] Sending notification.")
                send_email(ConfigLoader().load_config().smtp, f"[+] {target.message_subject}", target.message_body)
        elif target.alert_when_not_found and  found_match == Status.FOUND:
            event_result.reset()
            logger.info(f"[{target.target_id}] No interesting website content was found.")
        elif target.alert_when_found and found_match == Status.NOT_FOUND:
            event_result.reset()
            logger.info(f"[{target.target_id}] No interesting website content was found.")

