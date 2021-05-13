import mariadb
from hashlib import sha512


class DI:
    conn: mariadb._mariadb.connection

    def __init__(self, username):
        # get from db user access level

        pass
