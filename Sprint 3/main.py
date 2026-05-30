"""Sprint 3 application entrypoint."""

import os
import sys


app_source = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "app"
)
sys.path.insert(0, app_source)

from main import main


if __name__ == "__main__":
    main()
