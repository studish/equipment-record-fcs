#!/usr/bin/env python3

import webframework
from webframework import server
import api.main


server.serveStatic('/', './static')

if __name__ == "__main__":
    server.listen()
