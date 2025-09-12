"""
Factory to create crawlers with their dependencies
Hexagonal Architecture DDD - Infrastructure Layer
"""

import importlib.util
import inspect
import os
import sys
from pathlib import Path

class CrawlerFactory:
    """Factory to dynamically create all RSS crawlers in the crawlers directory"""

    @staticmethod
    def get_all_crawlers():
        """Dynamically discover and instantiate all available RSS crawlers"""
        crawlers = []
        crawlers_dir = Path(__file__).parent.parent / "external" / "crawlers"
        for file in crawlers_dir.glob("*_crawler.py"):
            module_name = file.stem
            spec = importlib.util.spec_from_file_location(module_name, str(file))
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            try:
                spec.loader.exec_module(module)
                # Find the concrete crawler class (ignore BaseCrawler)
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if name.lower().endswith("crawler") and name.lower() != "basecrawler" and obj.__module__ == module.__name__:
                        crawlers.append(obj())
                        break
            except Exception as e:
                print(f"Error loading crawler from {file.name}: {e}")
        return crawlers

    @staticmethod
    def get_available_sources():
        """Return list of available source names dynamically"""
        crawlers = CrawlerFactory.get_all_crawlers()
        return [crawler.source_name for crawler in crawlers]
