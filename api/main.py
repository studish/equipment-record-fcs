import urllib.parse

import webframework
from webframework import server
from utils import logger as logger
from dbinterface import DI
import os

db = DI.DI()


@server.get("/api/version")
def version(handler: webframework.RequestHandler):
    handler.send("1.0")


@server.post("/postrequest")
def postrequest(handler: webframework.RequestHandler):
    if not os.path.isdir("./files"):
        os.mkdir("./files")
    logger.debug(type(handler.post_files["excel"][0][1]))
    logger.debug(handler.post_files["excel"][0][1])
    handler.send({"success": True})


# for key in handler.post_files:
#     for file, filename in handler.post_files[key]:
#         logger.debug("Saving %s...", filename)
#         with open('./files/' + filename, 'wb') as f:
#             f.write(file)
#             f.close()
#             # "(.*)(\.*)?" // в базу добавлять (первые [100 - длина (. + расширение)]) + . + расширение
# handler.send({
#     "data": handler.post_data,
#     "files": [(key, [filename for _, filename in handler.post_files[key]]) for key in handler.post_files.keys()]
# })


@server.post("/api/login")
def login(handler: webframework.RequestHandler):
    try:
        username = handler.post_data["username"]
        password = handler.post_data["password"]
        logger.debug("username " + username)
        logger.debug("password " + password)
        success, error_message = db.authenticate_user(handler, username, password)

        handler.send(
            {
                "success": success,
                "errorMessage": error_message,
                "data": {
                    "authorized": handler.session.authorized,
                    "username": handler.session.username,
                    "adminRole": handler.session.admin,
                },
            }
        )
    except KeyError:
        handler.send({"success": False, "error_message": "wrong request body format"})
    except Exception as e:
        handler.send_error(400)


@server.post("/api/logout")
def logout(handler: webframework.RequestHandler):
    try:
        handler.session.authorized = False
        handler.session.username = ""
        handler.session.admin = False

        handler.send(
            {
                "success": True,
            }
        )
    except Exception as e:
        handler.send_error(400)


@server.get("/api/checkAuth")
def check_auth(handler: webframework.RequestHandler):
    try:
        handler.send(
            {
                "success": True,
                "data": {
                    "authorized": handler.session.authorized,
                    "username": handler.session.username,
                    "adminRole": handler.session.admin,
                },
            }
        )
    except Exception as e:
        handler.send_error(400)


@server.get("/api/user")
def get_user(handler: webframework.RequestHandler):
    try:
        success, error_message, user_data = db.get_user_by_id(handler.query["id"][0])

        handler.send(
            {"success": success, "errorMessage": error_message, "data": user_data}
        )
    except Exception as e:
        handler.send_error(400)


@server.get("/api/download")
def get_file(handler: webframework.RequestHandler):
    try:
        binary_data, file_name = db.get_file_by_id(handler.query["id"][0])

        if binary_data is not None:
            handler.response_headers.append(
                ("Content-Disposition", f'attachment; filename="{file_name}"')
            )
            handler.response_headers.append(
                ("Content-Type", "application/octet-stream")
            )
            handler.send(binary_data)
        elif file_name == "No such file":
            handler.send_error(404)
    except KeyError:
        handler.send_error(400)
    except Exception as e:
        logger.exception(e)
        handler.send_error(500)


@server.get("/api/users")
def get_users(handler: webframework.RequestHandler):
    success, error_message, user_data_list = db.get_user_list()

    handler.send(
        {"success": success, "errorMessage": error_message, "data": user_data_list}
    )


@server.get("/api/files")
def get_files(handler: webframework.RequestHandler):
    try:
        file_list = db.get_log_files(handler.query["logid"][0])

        handler.send({"success": True, "data": file_list})
    except Exception as e:
        logger.exception(e)


@server.get("/api/items")
def get_items(handler: webframework.RequestHandler):
    try:
        if "search" in handler.query.keys():
            search_query = handler.query["search"][0]
        else:
            search_query = ""

        if "categories" in handler.query:
            categories = handler.query["categories"][0].split(",")
        else:
            categories = []

        success, error_message, count, data = db.get_item_list(
            search=search_query,
            offset=handler.query["offset"][0],
            categories=categories,
        )
        handler.send(
            {
                "success": success,
                "errorMessage": error_message,
                "data": {"count": count, "items": data},
            }
        )
    except Exception as e:
        logger.exception(e)


@server.get("/api/logs")
def get_logs(handler: webframework.RequestHandler):
    try:
        success, error_message, data = db.get_logs(handler.query["itemid"][0])
        handler.send({"success": success, "errorMessage": error_message, "data": data})
    except Exception:
        handler.send_error(400)


@server.get("/api/generateFiles")
def get_inquiry_file_excel(handler: webframework.RequestHandler):
    try:
        binary_data, file_name = db.get_excel_file(handler.query["inqid"][0])

        if binary_data is not None:
            handler.response_headers.append(
                (
                    "Content-Disposition",
                    f'attachment; filename="{urllib.parse.quote(file_name)}"',
                )
            )
            handler.response_headers.append(
                ("Content-Type", "application/octet-stream")
            )
            handler.send(binary_data)
    except KeyError:
        handler.send_error(400)
        logger.exception("key error")
    except Exception as e:
        logger.exception(e)
        handler.send_error(500)


@server.get("/api/inquiries")
def get_inquiries(handler: webframework.RequestHandler):
    try:
        success, data = db.get_inquiries(
            status=handler.query["status"][0], offset=handler.query["offset"][0]
        )
        handler.send({"success": True, "errorMessage": "", "data": data})
    except Exception as e:
        logger.exception(e)
        handler.send({"success": False, "errorMessage": str(e)})


@server.post("/api/inquiry")
def create_inquiry(handler: webframework.RequestHandler):
    try:
        success, error_message, data = db.create_inquiry(inquiry_data=handler.post_data)
        # logger.debug(success, error_message, data)

        handler.send({"success": success, "errorMessage": error_message, "data": data})
    except Exception as e:
        logger.exception(e)
        handler.send({"success": False, "errorMessage": str(e)})


@server.post("/api/item")
def create_item(handler: webframework.RequestHandler):
    try:
        success, error_message, data = db.create_item(item_data=handler.post_data)

        handler.send({"success": success, "errorMessage": error_message, "data": data})
    except Exception as e:
        logger.exception(e)
        handler.send({"success": False, "errorMessage": str(e)})


@server.put("/api/item")
def update_item(handler: webframework.RequestHandler):
    try:
        success, error_message, data = db.update_item(handler.post_data)

        handler.send({"success": success, "errorMessage": error_message, "data": data})
    except Exception as e:
        logger.exception(e)
        handler.send({"success": False, "errorMessage": str(e)})


@server.patch("/api/inquiry")
def update_inquiry(handler: webframework.RequestHandler):
    try:
        success, error_message, data = db.update_inquiry(handler.post_data)

        handler.send({"success": success, "errorMessage": error_message, "data": data})
    except Exception as e:
        logger.exception(e)
        handler.send({"success": False, "errorMessage": str(e)})


@server.post("/api/log")
def create_log(handler: webframework.RequestHandler):
    try:
        success, error_message, data = db.create_log(
            post_data=handler.post_data, post_files=handler.post_files
        )
        handler.send({"success": success, "errorMessage": error_message, "data": data})
    except Exception as e:
        logger.exception(e)
        handler.send({"success": False, "errorMessage": str(e)})
