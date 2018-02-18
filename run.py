import sys
import os
from server import Server

if __name__ == "__main__":
    argv = sys.argv
    USAGE = "Usage: python3 run.py <port> <path_to_db>"

    if len(argv) != 3:
        print(USAGE)
        sys.exit(1)

    port = int(argv[1])
    path_to_db = argv[2]
    template_dir = os.path.abspath('templates')
    server = Server(port, path_to_db, template_dir)
    server.run()
