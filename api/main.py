import webframework
from webframework import server
from utils import logger as logger
import os


def checkauth(handler: webframework.RequestHandler):
    if handler.session.sid not in server.sessions.keys():
        handler.redirect_to("/login")
        return False
    # TODO: Check if authorized
    return True


@server.get("/api/version", middleware=[checkauth])
def version(handler: webframework.RequestHandler):
    handler.send("1.0")


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
    for key in handler.post_files:
        for file, filename in handler.post_files[key]:
            logger.debug("Saving %s...", filename)
            with open('./files/' + filename, 'wb') as f:
                f.write(file)
                f.close()
    handler.send({
        "data": handler.post_data,
        "files": [(key, [filename for _, filename in handler.post_files[key]]) for key in handler.post_files.keys()]
    })


@server.get('/unicodeTest')
def uwu(handler):
    handler.send(
        '<h1>ТЕСТ</h1><p>Если это видно, значит юникод обрабатывается корректно!</p><img src="./favicon.ico" />')
