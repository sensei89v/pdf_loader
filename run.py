import sys
import os
from server import Server

if __name__ == "__main__":
    argv = sys.argv
    USAGE = "Usage: python3 run.py <port> <path_to_db>"

    if len(argv) != 3:
        print(USAGE)
        sys.exit(1)

    try:
        port = int(argv[1])
    except:
        print("port should be between 0 and 65535")
        sys.exit(1)

    if port < 0 and port > 65535:
        print("port should be between 0 and 65535")
        sys.exit(1)

    path_to_db = argv[2]
    template_dir = os.path.abspath('templates')
    server = Server(port, path_to_db, template_dir)
    server.run()
