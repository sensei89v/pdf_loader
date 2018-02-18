import sys
import os
from db import DBEngine

if __name__ == "__main__":
    argv = sys.argv

    if len(argv) != 2:
        print("Usage: %s <path_to_db>" % argv[0])
        sys.exit(1)

    path_to_db = os.path.abspath(argv[1])
    engine = DBEngine(path_to_db)
    engine.create_db()
