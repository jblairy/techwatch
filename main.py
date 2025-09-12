#!/usr/bin/env python3
"""
Main entry point - Hexagonal Architecture DDD
Technology watch tool with separated architecture
"""

import sys
import os

# Add root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.presentation.cli.veille_cli import main as cli_main

def main():
    """Main entry point using hexagonal architecture DDD"""
    try:
        cli_main()
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
