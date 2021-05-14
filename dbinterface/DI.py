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
            cur.execute("SELECT login, user_type FROM equipment_record.user WHERE login=? AND password_hash=?",
                        (username, sha512(password.encode()).hexdigest()))
            for login, user_type in cur:
                if user_type[0] == 'ADMIN':
                    handler.session.admin = True

            handler.session.authorized = True
            handler.session.username = username

            conn.close()
        except Exception as e:
            logger.exception(e)
