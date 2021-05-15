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
            password_hash = sha512(password.encode()).hexdigest()
            cur.execute(
                "SELECT login, password_hash, user_type "
                "FROM equipment_record_fcs.user "
                "WHERE login=? AND password_hash=?",
                (username, password_hash))

            for login, password_hash, user_type in cur:
                if login == username and password_hash == password_hash:
                    if user_type[0] == 'ADMIN':
                        handler.sion.admin = True
                    handler.session.authorized = True
                    handler.session.username = username
                    return True, ""

            conn.close()
        except Exception as e:
            return False, str(e)
        return False, "Incorrect credentials."

    @staticmethod
    def get_user(user_id: str):
        try:
            conn, cur = dbconnect.connection('erfcs_admin')
            cur.execute("SELECT id, user_type, display_name FROM equipment_record_fcs.user WHERE user.id=?",
                        (int(user_id),))

            for _id, user_type, display_name in cur:
                return True, "", {
                    "id": _id,
                    "user_type": user_type,
                    "display_name": display_name
                }

            conn.close()
        except Exception as e:
            return False, str(e), None
        return False, "No such user.", None
