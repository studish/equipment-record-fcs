import webframework
from webframework import server
from utils import logger as logger
import os
from dbinterface import DI

db = DI.DI()


# def checkauth(handler: webframework.RequestHandler):
#     if handler.session.sid not in server.sessions.keys():
#         handler.redirect_to("/login")
#         return False
#     # Check if authorized ?to do?
#     return True
# @server.get("/api/path", middlewares=[checkauth])


@server.get("/api/version")
def version(handler: webframework.RequestHandler):
    handler.send("1.0")


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
                # "(.*)(\.*)?" // в базу добавлять (первые [100 - длина (. + расширение)]) + . + расширение
    handler.send({
        "data": handler.post_data,
        "files": [(key, [filename for _, filename in handler.post_files[key]]) for key in handler.post_files.keys()]
    })


@server.get('/unicodeTest')
def uwu(handler):
    handler.send(
        '<h1>ТЕСТ</h1><p>Если это видно, значит юникод обрабатывается корректно!</p><img src="./favicon.ico" />')


@server.post('/api/login')
def login(handler: webframework.RequestHandler):
    username = handler.post_data["username"][0]
    password = handler.post_data["password"][0]

    db.authenticate_user(handler, username, password)

    handler.send({
        "authorized": handler.session.authorized,
        "username": handler.session.username,
        "adminRole": handler.session.admin,
    })


@server.post('/api/logout')
def logout(handler: webframework.RequestHandler):
    handler.session.authorized = False
    handler.session.username = ""
    handler.session.admin = False

    handler.send({
        "authorized": handler.session.authorized,
        "username": handler.session.username,
        "adminRole": handler.session.admin,
    })


@server.get('/api/checkAuth')
def checkauth(handler: webframework.RequestHandler):
    handler.send({
        "authorized": handler.session.authorized,
        "username": handler.session.username,
        "adminRole": handler.session.admin,
    })
