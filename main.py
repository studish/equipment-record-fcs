#!/usr/bin/env python3

import webframework
from utils import webServerLogger as logger
import os


server = webframework.Server()


@server.get('/api/jsonExample')
def index(handler: webframework.RequestHandler):
    handler.send({
        "key": "value",
        "numkey": 1,
        "boolkey": True
    })


@server.post('/postrequest')
def postrequest(handler: webframework.RequestHandler):
    if not os.path.isdir('./files'):
        os.mkdir('./files')
    for key in handler.postFiles:
        for file, filename in handler.postFiles[key]:
            logger.debug("Saving %s...", filename)
            with open('./files/' + filename, 'wb') as f:
                f.write(file)
                f.close()
    handler.send({
        "data": handler.postData,
        "files": [(key, [filename for _, filename in handler.postFiles[key]]) for key in handler.postFiles.keys()]
    })


server.serveStatic('/', './static')

if __name__ == "__main__":
    server.listen()
