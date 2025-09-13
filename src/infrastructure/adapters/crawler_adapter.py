"""
Crawler adapter - Infrastructure
Hexagonal DDD Architecture
"""
import logging
from typing import List, Dict, Any
from pathlib import Path

from ...domain.repositories.post_repository import CrawlerRepository


class FileCrawlerRepository(CrawlerRepository):
    """
    Concrete implementation of the repository for crawler management.

    This class manages crawler configuration and state via files.
    """

    def __init__(self, config_directory: str = "config"):
        self.config_directory = Path(config_directory)
        self.config_directory.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def get_all_active_crawlers(self) -> List[str]:
        """Returns the list of active crawlers (dynamically from the crawlers directory)"""
        crawlers_dir = self.config_directory.parent / "external" / "crawlers"
        active_crawlers = []
        for file in crawlers_dir.glob("*_crawler.py"):
            name = file.stem.replace('_crawler', '').replace('_', '-')
            config = self.get_crawler_config(name)
            if config.get('enabled', True):
                active_crawlers.append(name)
        return active_crawlers

    def get_crawler_config(self, crawler_name: str) -> Dict[str, Any]:
        """Returns the configuration of a specific crawler"""
        config_file = self.config_directory / f"{crawler_name}.json"

        # Default configuration
        default_config = {
            'name': crawler_name,
            'enabled': True,
            'timeout': 10,
            #'headers': {
            #    'User-Agent': 'Mozilla/5.0 (compatible; Techwatch/2.0)'
            #},
            'retry_count': 3,
            'retry_delay': 1
        }

        if config_file.exists():
            try:
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                default_config.update(file_config)
            except Exception as e:
                self.logger.warning(f"Error reading config {crawler_name}: {e}")

        return default_config

    def is_crawler_enabled(self, crawler_name: str) -> bool:
        """Checks if a crawler is enabled"""
        config = self.get_crawler_config(crawler_name)
        return config.get('enabled', True)

    def save_crawler_config(self, crawler_name: str, config: Dict[str, Any]) -> None:
        """Saves the configuration of a crawler"""
        config_file = self.config_directory / f"{crawler_name}.json"

        try:
            import json
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Configuration saved for {crawler_name}")
        except Exception as e:
            self.logger.error(f"Error saving config {crawler_name}: {e}")

    def disable_crawler(self, crawler_name: str) -> None:
        """Disables a crawler"""
        config = self.get_crawler_config(crawler_name)
        config['enabled'] = False
        self.save_crawler_config(crawler_name, config)

    def enable_crawler(self, crawler_name: str) -> None:
        """Enables a crawler"""
        config = self.get_crawler_config(crawler_name)
        config['enabled'] = True
        self.save_crawler_config(crawler_name, config)
