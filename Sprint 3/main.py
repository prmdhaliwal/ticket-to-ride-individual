"""Sprint 3 application entrypoint."""

import os
import sys


sprint_2_source = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "Sprint 2"
)
sys.path.insert(0, sprint_2_source)

from main import main


if __name__ == "__main__":
    main()
