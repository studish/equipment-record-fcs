import json

import mariadb
from hashlib import sha512
from utils.Logger import logger
from typing import List

import dbconnect


class DI:
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
    def get_user_by_id(user_id: str):
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

    @staticmethod
    def get_file_by_id(file_id: str) -> tuple[bytes, str]:
        try:
            conn, cur = dbconnect.connection('erfcs_admin')
            cur.execute("SELECT `blob`, `filename` FROM `equipment_record_fcs`.`file` WHERE `file`.`id`=?",
                        (int(file_id),))
            for file, file_name in cur:
                return file, file_name

            conn.close()
        except Exception as e:
            raise e
        return b'', "No such file"

    @staticmethod
    def get_user_list():
        try:
            user_data_list = []
            conn, cur = dbconnect.connection('erfcs_admin')
            cur.execute("SELECT id, user_type, display_name FROM equipment_record_fcs.user")

            for _id, user_type, display_name in cur:
                user_data_list.append({
                    "id": _id,
                    "user_type": user_type,
                    "display_name": display_name
                })

            conn.close()
            if len(user_data_list) > 0:
                return True, "", user_data_list
            else:
                return False, "No users.", None
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def get_log_files(logid: str):
        try:
            log_file_list = []
            conn, cur = dbconnect.connection('erfcs_admin')
            cur.execute("SELECT `id`, `filename` FROM `equipment_record_fcs`.`file` WHERE `file`.`log`=?",
                        (int(logid),))
            for file_id, file_name in cur:
                log_file_list.append({
                    "id": file_id,
                    "fileName": file_name
                })

            conn.close()
            return log_file_list
        except Exception as e:
            raise e

    @staticmethod
    def get_item_list(search: str = '', offset: str = 0, categories: List[str] = []):
        try:
            invitem_list = []
            conn, cur = dbconnect.connection('erfcs_admin')
            query = "SELECT * FROM inventoryitem "
            query += "WHERE (inventoryitem.display_name REGEXP ? " \
                     "OR inventoryitem.category REGEXP ? " \
                     "OR inventoryitem.invid REGEXP ? " \
                     "OR inventoryitem.serial_num REGEXP ?) "
            if categories:
                query += "AND (inventoryitem.category IN (" + ", ".join(["?"] * len(categories)) + ")) "
                cur.execute(query, (search, search, search, search, *categories))
            else:
                cur.execute(query, (search, search, search, search))
            query += "LIMIT 20 OFFSET ?"

            for id, invid, category, display_name, serial_num, price, available, desc in cur:
                invitem_list.append({
                    "id": id,
                    "invid": invid,
                    "category": category,
                    "displayName": display_name,
                    "serial_num": serial_num,
                    "price": price,
                    "available": price,
                    "description": desc
                })
            cur.execute("SELECT FOUND_ROWS()")
            (count, ) = cur.fetchone()
            conn.close()
            return True, "", count, invitem_list
        except Exception as e:
            return False, str(e), 0, []

    @staticmethod
    def get_logs(itemid):
        try:
            data = []
            conn, cur = dbconnect.connection('erfcs_admin')
            cur.execute(
                "SELECT log.id, log.description, log.timestamp, GROUP_CONCAT('{\"fileName\": \"', "
                "file.filename, '\", \"id\": ', file.id, '}' SEPARATOR ', ') as data "
                "FROM `equipment_record_fcs`.`log` "
                "INNER JOIN `equipment_record_fcs`.`file` ON  log.item_id=? AND log.id = file.log", (int(itemid),))
            for logid, description, timestamp, file_json_list in cur:
                data.append({
                    "id": logid,
                    "description": description,
                    "timestamp": str(timestamp),
                    "itemId": itemid,
                    "files": json.loads(f'[{file_json_list}]')
                })
            conn.close()
            return True, "", data
        except Exception as e:
            raise e

    @staticmethod
    def get_excel_file(inqid):
        try:
            conn, cur = dbconnect.connection('erfcs_admin')
            cur.execute(
                "SELECT inquirername "
                "FROM equipment_record_fcs.inquiry "
                "WHERE inquiry.id=?",
                (int(inqid),))

            with open('files/накладная.xlsx', 'rb') as f:
                binary_data = f.read()
                for name in cur:
                    file_name = f'требование_накладная_{name[0]}.xlsx'

            conn.close()
            return binary_data, file_name

        except Exception as e:
            raise e

    @staticmethod
    def get_inquiries(status, offset):
        try:
            inquiries = []
            conn, cur = dbconnect.connection('erfcs_admin')
            cur.execute(
                "SELECT inquiry.id, inquiry.inquirername, inquiry.inquireremail, inquiry.comment, "
                "inquiry.status, inquiry.inventory_item "
                "FROM equipment_record_fcs.inquiry "
                "WHERE inquiry.status=? "
                "LIMIT 20 "
                "OFFSET ?", (status, int(offset)))

            for id, inquirername, inquireremail, comment, status, inventory_item in cur:
                inquiries.append({
                    'id': id,
                    "inquirerName": inquirername,
                    "inquirerEmail": inquireremail,
                    "comment": comment,
                    "status": status,
                    "itemId": inventory_item
                })

            conn.close()
            return True, inquiries

        except Exception as e:
            raise
