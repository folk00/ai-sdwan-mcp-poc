from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from mcp_server.tool_catalog import TOOL_CATALOG


if __name__ == "__main__":
    print(json.dumps({"tools": TOOL_CATALOG}, indent=2))
