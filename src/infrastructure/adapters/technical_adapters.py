"""
Technical Adapters - Infrastructure Layer
Hexagonal Architecture DDD
"""
import requests
import logging
from datetime import datetime, date
from bs4 import BeautifulSoup
from typing import List

logger = logging.getLogger(__name__)


class RequestsHttpClient:
    """HTTP Client based on requests - Infrastructure Layer"""

    def __init__(self, timeout: int = 10, headers: dict = None):
        self.timeout = timeout
        self.headers = headers or {}

    def get(self, url: str) -> requests.Response:
        try:
            response = requests.get(url, timeout=self.timeout, headers=self.headers)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"HTTP request error to {url}: {e}")
            raise


class BeautifulSoupParser:
    """HTML Parser based on BeautifulSoup - Infrastructure Layer"""

    def __init__(self, parser: str = "html.parser"):
        self.parser = parser

    def parse(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, self.parser)


class SystemDateProvider:
    """Current date provider - Infrastructure Layer"""

    def get_current_date(self) -> date:
        return datetime.today().date()

    def today(self) -> date:
        """Alias for get_current_date for compatibility"""
        return self.get_current_date()
