import sys
import os
from db import DBEngine

if __name__ == "__main__":
    argv = sys.argv

    if len(argv) != 4:
        print("Usage: %s <path_to_db> <user_name> <password>" % argv[0])
        sys.exit(1)

    path_to_db = os.path.abspath(argv[1])
    engine = DBEngine(path_to_db)
    engine.add_user_to_db(argv[2], argv[3])
