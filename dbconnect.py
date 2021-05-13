import mariadb
import configparser


def connection(user: str) -> tuple:
    config = configparser.ConfigParser()
    config.read('credentials.properties')

    conn = mariadb.connect(
        host='localhost',
        user=user,
        password=config.get('PasswordSection', user),
        port=3306,
        db='equipment_record'
    )

    cur = conn.cursor()

    return conn, cur
