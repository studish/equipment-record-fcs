#!/usr/bin/env python3

import webframework


server = webframework.Server()


@server.get('/')
def index(handler: webframework.RequestHandler):
    handler.send('<h1>Hello, World!</h1>')


if __name__ == "__main__":
    server.listen()
