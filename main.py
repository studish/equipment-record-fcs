#!/usr/bin/env python3

import webframework


server = webframework.Server()


@server.get('/api/jsonExample')
def index(handler: webframework.RequestHandler):
    handler.send({
        "key": "value",
        "numkey": 1,
        "boolkey": True
    })


server.serveStatic('/', './static')

if __name__ == "__main__":
    server.listen()
