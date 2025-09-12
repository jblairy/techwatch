"""
CLI Interface - Presentation Layer
Hexagonal Architecture DDD

This CLI is designed to interact with a single, robust database file (veille_db.json).
All commands operate on this unified source, ensuring maintainability and eliminating user confusion about file selection.
All documentation and help messages are in English for consistency and accessibility.
"""
import argparse
import logging
import sys
from typing import Optional, List

from ...application.use_cases.veille_use_cases import (
    LoadWatchDataUseCase,
    SaveWatchDataUseCase,
    AnalyzeWatchDataUseCase
)
from ...application.dto.post_dto import VeilleRequestDTO
from ...infrastructure.repositories.json_post_repository import JsonPostRepository
from ...infrastructure.adapters.crawler_adapter import FileCrawlerRepository


class TechWatchCLI:
    """
    Command line interface for the technology watch tool.

    All operations use a single database file (veille_db.json).
    No file selection is required; all results and analyses are performed on the latest data.
    """

    def __init__(self):
        # Dependency injection (infrastructure)
        self.post_repository = JsonPostRepository()
        self.crawler_repository = FileCrawlerRepository()

        # Use cases initialization (application)
        self.load_use_case = LoadWatchDataUseCase(self.post_repository)
        self.save_use_case = SaveWatchDataUseCase(self.post_repository)
        self.analyze_use_case = AnalyzeWatchDataUseCase(self.post_repository)

        self.logger = logging.getLogger(__name__)

    def setup_logging(self, verbose: bool = False, quiet: bool = False):
        """
        Configure logging for CLI output.
        """
        if quiet:
            level = logging.WARNING
        elif verbose:
            level = logging.DEBUG
        else:
            level = logging.INFO

        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )

    def create_parser(self) -> argparse.ArgumentParser:
        """
        Create the argument parser for the CLI.
        Only relevant options for a single database are presented.
        """
        parser = argparse.ArgumentParser(
            description="Technology Watch Tool - Hexagonal Architecture DDD",
            epilog="Use 'command --help' for more information on a specific command."
        )
        parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
        parser.add_argument('--quiet', '-q', action='store_true', help='Enable quiet mode (warnings only)')
        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # Show command
        show_parser = subparsers.add_parser('show', help='Show technology watch results from the database')
        show_parser.add_argument('--days-back', type=int, help='Filter by number of days back')
        show_parser.add_argument('--source', help='Filter by source name')
        show_parser.add_argument('--limit', type=int, help='Limit number of results')

        # Analyze command
        analyze_parser = subparsers.add_parser('analyze', help='Analyze technology watch data from the database')
        analyze_parser.add_argument('--days-back', type=int, help='Filter by number of days back')
        analyze_parser.add_argument('--source', help='Filter by source name')

        return parser

    def run_show_command(self, args):
        """
        Execute the show command using the unified database.
        """
        try:
            request = VeilleRequestDTO(
                days_back=args.days_back,
                source_filter=args.source,
                limit=args.limit
            )
            result = self.load_use_case.load_latest(request)
            if not result.posts:
                print("📭 No articles found with the specified criteria.")
                return
            posts = [dto.to_entity() for dto in result.posts]
            if args.limit:
                posts = posts[:args.limit]
            posts_by_source = {}
            for post in posts:
                source = post.source or "Unknown source"
                if source not in posts_by_source:
                    posts_by_source[source] = []
                posts_by_source[source].append(post)
            print(f"📊 {len(posts)} articles found")
            print(f"🎯 {len(posts_by_source)} sources\n")
            for source, source_posts in posts_by_source.items():
                print(f"📍 {source} ({len(source_posts)} articles)")
                for post in source_posts:
                    print(f"  ✅ {post.title}")
                    print(f"  🔗 {post.url}")
                    if post.date:
                        print(f"  📅 {post.date}")
                    print()
        except Exception as e:
            self.logger.error(f"Error showing results: {e}")
            print(f"❌ Error: {e}")
            sys.exit(1)

    def run_analyze_command(self, args):
        """
        Execute the analyze command using the unified database.
        """
        try:
            request = VeilleRequestDTO(
                days_back=args.days_back,
                source_filter=args.source
            )
            result = self.analyze_use_case.analyze_latest(request)
            print("📊 TECHNOLOGY WATCH ANALYSIS\n")
            print(f"Total articles: {result['total_posts']}")
            print(f"Date range: {result['date_range']['start']} → {result['date_range']['end']}")
            print(f"Duration: {result['date_range']['duration_days']} days\n")
            print("📍 SOURCES SUMMARY:")
            sources_summary = result['sources_summary']
            for source, count in sorted(sources_summary.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {source}: {count} articles")
            print(f"\n📋 Metadata:")
            metadata = result['metadata']
            print(f"  Generated: {metadata.get('generated_at', 'Unknown')}")
            print(f"  Format version: {metadata.get('format_version', 'Unknown')}")
        except Exception as e:
            self.logger.error(f"Error analyzing results: {e}")
            print(f"❌ Error: {e}")
            sys.exit(1)

    def run(self):
        """
        Main CLI execution entry point.
        """
        parser = self.create_parser()
        args = parser.parse_args()
        self.setup_logging(args.verbose, args.quiet)
        if not args.command:
            parser.print_help()
            return
        try:
            if args.command == 'show':
                self.run_show_command(args)
            elif args.command == 'analyze':
                self.run_analyze_command(args)
            else:
                print(f"❌ Unknown command: {args.command}")
                sys.exit(1)
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
            sys.exit(0)


def main():
    """
    CLI entry point.
    """
    cli = TechWatchCLI()
    cli.run()


if __name__ == "__main__":
    main()
