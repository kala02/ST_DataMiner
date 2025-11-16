
"""Convenience script to run the ST data miner."""

import sys
from pathlib import Path

# Add the scripts directory to Python path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from cli import main

if __name__ == "__main__":
    sys.exit(main())
