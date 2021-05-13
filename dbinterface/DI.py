import mariadb
from hashlib import sha512
from utils.Logger import logger

import dbconnect


class DI:
    conn: mariadb._mariadb.connection

    def __init__(self):
        # get from db user access level
        pass

    @staticmethod
    def authenticate_user(handler, username: str, password: str):
        try:
            conn, cur = dbconnect.connection('erfcs_admin')
            cur.execute("SELECT user_type FROM test.contacts", (username, password))
            # if authentication successful
            # execute select and if username and password are correct then True
            # handler.session.authorized = True
            # handler.session.username = username
            # handler.admin = from db response

            conn.close()
        except Exception as e:
            logger.exception(e)
