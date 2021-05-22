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
            conn, cur = dbconnect.connection("erfcs_admin")
            password_hash = sha512(password.encode()).hexdigest()
            cur.execute(
                "SELECT login, password_hash, user_type "
                "FROM equipment_record_fcs.user "
                "WHERE login=? AND password_hash=?",
                (username, password_hash),
            )

            for login, password_hash, user_type in cur:
                if login == username and password_hash == password_hash:
                    if user_type == "ADMIN":
                        handler.session.admin = True
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
            conn, cur = dbconnect.connection("erfcs_admin")
            cur.execute(
                "SELECT id, user_type, display_name FROM equipment_record_fcs.user WHERE user.id=?",
                (int(user_id),),
            )

            for _id, user_type, display_name in cur:
                return (
                    True,
                    "",
                    {"id": _id, "user_type": user_type, "display_name": display_name},
                )

            conn.close()
        except Exception as e:
            return False, str(e), None
        return False, "No such user.", None

    @staticmethod
    def get_file_by_id(file_id: str) -> tuple[bytes, str]:
        try:
            conn, cur = dbconnect.connection("erfcs_admin")
            cur.execute(
                "SELECT `blob`, `filename` FROM `equipment_record_fcs`.`file` WHERE `file`.`id`=?",
                (int(file_id),),
            )
            for file, file_name in cur:
                return file, file_name

            conn.close()
        except Exception as e:
            raise e
        return b"", "No such file"

    @staticmethod
    def get_user_list():
        try:
            user_data_list = []
            conn, cur = dbconnect.connection("erfcs_admin")
            cur.execute(
                "SELECT id, user_type, display_name FROM equipment_record_fcs.user"
            )

            for _id, user_type, display_name in cur:
                user_data_list.append(
                    {"id": _id, "user_type": user_type, "display_name": display_name}
                )

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
            conn, cur = dbconnect.connection("erfcs_admin")
            cur.execute(
                "SELECT `id`, `filename` FROM `equipment_record_fcs`.`file` WHERE `file`.`log`=?",
                (int(logid),),
            )
            for file_id, file_name in cur:
                log_file_list.append({"id": file_id, "fileName": file_name})

            conn.close()
            return log_file_list
        except Exception as e:
            raise e

    @staticmethod
    def get_item_list(search: str = "", offset: str = 0, categories: List[str] = [], authorized: bool = False):
        try:
            invitem_list = []
            conn, cur = dbconnect.connection("erfcs_admin")
            query = "SELECT * FROM inventoryitem "
            query += (
                "WHERE (inventoryitem.display_name REGEXP ? "
                "OR inventoryitem.category REGEXP ? "
                "OR inventoryitem.invid REGEXP ? "
                "OR inventoryitem.serial_num REGEXP ?) "
            )
            if not authorized:
                query += "AND `available`=1 "
            if categories:
                query += (
                        "AND (inventoryitem.category IN ("
                        + ", ".join(["?"] * len(categories))
                        + ")) "
                )
                query += "LIMIT 20 OFFSET ?"
                cur.execute(query, (search, search, search, search, *categories, offset))
            else:
                query += "LIMIT 20 OFFSET ?"
                cur.execute(query, (search, search, search, search, offset))

            for (
                    id,
                    invid,
                    category,
                    display_name,
                    serial_num,
                    price,
                    available,
                    desc,
            ) in cur:
                invitem_list.append(
                    {
                        "id": id,
                        "invid": invid,
                        "category": category,
                        "displayName": display_name,
                        "serial_num": serial_num,
                        "price": price,
                        "available": available,
                        "description": desc,
                    }
                )

            query = "SELECT * FROM inventoryitem "
            query += (
                "WHERE (inventoryitem.display_name REGEXP ? "
                "OR inventoryitem.category REGEXP ? "
                "OR inventoryitem.invid REGEXP ? "
                "OR inventoryitem.serial_num REGEXP ?) "
            )
            if not authorized:
                query += "AND `available`=1 "
            if categories:
                query += (
                        "AND (inventoryitem.category IN ("
                        + ", ".join(["?"] * len(categories))
                        + ")) "
                )
                cur.execute(query, (search, search, search, search, *categories, offset))
            else:
                cur.execute(query, (search, search, search, search, offset))

            cur.execute("SELECT FOUND_ROWS()")
            (count,) = cur.fetchone()
            conn.close()
            return True, "", count, invitem_list
        except Exception as e:
            return False, str(e), 0, []

    @staticmethod
    def get_logs(itemid):
        try:
            data = []
            conn, cur = dbconnect.connection("erfcs_admin")
            cur.execute(
                'SELECT log.id, log.description, log.timestamp, GROUP_CONCAT(\'{"fileName": "\', '
                "file.filename, '\", \"id\": ', file.id, '}' SEPARATOR ', ') as data "
                "FROM `equipment_record_fcs`.`log` "
                "INNER JOIN `equipment_record_fcs`.`file` ON  log.item_id=? AND log.id = file.log GROUP BY log.id",
                (int(itemid),),
            )
            for logid, description, timestamp, file_json_list in cur:
                data.append(
                    {
                        "id": logid,
                        "description": description,
                        "timestamp": str(timestamp),
                        "itemId": itemid,
                        "files": json.loads(f"[{file_json_list}]"),
                    }
                )
            conn.close()
            return True, "", data
        except Exception as e:
            raise e

    @staticmethod
    def get_excel_file(inqid):
        try:
            conn, cur = dbconnect.connection("erfcs_admin")
            cur.execute(
                "SELECT inquirername "
                "FROM equipment_record_fcs.inquiry "
                "WHERE inquiry.id=?",
                (int(inqid),),
            )

            with open("files/накладная.xlsx", "rb") as f:
                binary_data = f.read()
                for name in cur:
                    file_name = f"требование_накладная_{name[0]}.xlsx"

            conn.close()
            return binary_data, file_name

        except Exception as e:
            raise e

    @staticmethod
    def get_inquiries(status, offset):
        try:
            inquiries = []
            conn, cur = dbconnect.connection("erfcs_admin")
            cur.execute(
                "SELECT inquiry.id, inquiry.inquirername, inquiry.inquireremail, inquiry.comment, "
                "inquiry.status, inquiry.inventory_item "
                "FROM equipment_record_fcs.inquiry "
                "WHERE inquiry.status=? "
                "LIMIT 20 "
                "OFFSET ?",
                (status, int(offset)),
            )

            for id, inquirername, inquireremail, comment, status, inventory_item in cur:
                inquiries.append(
                    {
                        "id": id,
                        "inquirerName": inquirername,
                        "inquirerEmail": inquireremail,
                        "comment": comment,
                        "status": status,
                        "itemId": inventory_item,
                    }
                )

            conn.close()
            return True, inquiries

        except Exception as e:
            raise

    @staticmethod
    def create_inquiry(inquiry_data):
        try:
            conn, cur = dbconnect.connection("erfcs_admin")
            cur.execute(
                "INSERT INTO `equipment_record_fcs`.`inquiry` "
                "(inquirername, inquireremail, comment, status, inventory_item) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    inquiry_data["inquirerName"][0],
                    inquiry_data["inquirerEmail"][0],
                    inquiry_data["comment"][0],
                    inquiry_data["status"][0],
                    int(inquiry_data["itemId"][0]),
                ),
            )
            conn.commit()
            cur.execute(
                "SELECT * FROM `equipment_record_fcs`.`inquiry` "
                "WHERE `inquirername`=? AND `inquireremail`=? AND "
                "`comment`=? AND `status`=? AND `inventory_item`=?",
                (
                    inquiry_data["inquirerName"][0],
                    inquiry_data["inquirerEmail"][0],
                    inquiry_data["comment"][0],
                    inquiry_data["status"][0],
                    int(inquiry_data["itemId"][0]),
                ),
            )
            data = {}
            for id, inquirername, inquireremail, comment, status, invid in cur:
                data = {
                    "id": id,
                    "inquirerName": inquirername,
                    "inquirerEmail": inquireremail,
                    "comment": comment,
                    "status": status,
                    "itemId": invid,
                }

            conn.close()

            return True, "", data
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def create_item(item_data):
        try:
            conn, cur = dbconnect.connection("erfcs_admin")
            logger.debug(f'{item_data["invid"]}, {item_data["price"]}')
            cur.execute(
                "INSERT INTO `equipment_record_fcs`.`inventoryitem` "
                "(invid, category, display_name, serial_num, price, available, description) "
                "VALUES (?, ?, ?, ?, ?, ?,?)",
                (
                    item_data["invid"][0],
                    item_data["category"][0],
                    item_data["displayName"][0],
                    item_data["serial_num"][0],
                    float(item_data["price"][0]),
                    item_data["available"][0],
                    item_data["description"][0],
                ),
            )
            conn.commit()
            cur.execute("SELECT LAST_INSERT_ID()")
            logid = -1
            for (log_id,) in cur:
                logid = log_id
            if logid < 0:
                return False, "Failed to create log"
            data = {
                "id": logid,
                "invid": item_data["invid"][0],
                "category": item_data["category"][0],
                "displayName": item_data["displayName"][0],
                "description": item_data["description"][0],
                "serial_num": item_data["serial_num"][0],
                "price": float(item_data["price"][0]),
                "available": 1
            }

            conn.close()
            return True, "", data
        except Exception as e:
            logger.exception(e)
            return False, str(e), None

    @staticmethod
    def update_item(item_data):
        conn = None
        try:
            conn, cur = dbconnect.connection("erfcs_admin")
            cur.execute(
                "UPDATE `equipment_record_fcs`.`inventoryitem` "
                "SET invid=?, category=?, display_name=?, serial_num=?, price=?, available=?, description=? "
                "WHERE `id`=?",
                (
                    item_data["invid"][0],
                    item_data["category"][0],
                    item_data["displayName"][0],
                    item_data["serial_num"][0],
                    float(item_data["price"][0]),
                    item_data["available"][0],
                    item_data["description"][0],
                    item_data["id"][0],
                ),
            )

            conn.commit()
            if cur.rowcount == 0:
                return False, "couldn't find the specifed item", {}
            data = {
                "id": item_data["id"][0],
                "invid": item_data["invid"][0],
                "category": item_data["category"][0],
                "displayName": item_data["displayName"][0],
                "description": item_data["description"][0],
                "serial_num": item_data["serial_num"][0],
                "price": item_data["price"][0],
                "available": item_data["available"][0],
            }
            return True, "", data
        except Exception as e:
            logger.exception(e)
            return False, str(e), None
        finally:
            if conn is not None:
                conn.close()

    @staticmethod
    def update_inquiry(updated_data):
        try:
            conn, cur = dbconnect.connection("erfcs_admin")
            cur.execute(
                "UPDATE `equipment_record_fcs`.`inquiry` "
                "SET status=? "
                "WHERE inquiry.id=?",
                (updated_data["status"], int(updated_data["itemId"])),
            )
            conn.commit()
            cur.execute(
                "SELECT * " "FROM `equipment_record_fcs`.`inquiry` " "WHERE `id`=?",
                (int(updated_data["itemId"][0]),),
            )
            data = {}
            for id, inquirername, inquireremail, comment, status, invid in cur:
                data = {
                    "id": id,
                    "inquirerName": inquirername,
                    "inquirerEmail": inquireremail,
                    "comment": comment,
                    "status": status,
                    "itemId": invid,
                }

            conn.close()

            return True, "", data
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def create_log(post_data, post_files):
        try:
            conn, cur = dbconnect.connection("erfcs_admin")
            cur.execute(
                "INSERT INTO `equipment_record_fcs`.`log`"
                "(item_id, timestamp, description) "
                "VALUES (?,?,?)",
                (
                    int(post_data["itemId"][0]),
                    post_data["timestamp"][0],
                    post_data["description"][0],
                ),
            )
            conn.commit()
            cur.execute("SELECT LAST_INSERT_ID()")
            logid = -1
            for (log_id,) in cur:
                logid = log_id
            if logid < -1:
                return False, "failed to add", {}
            conn.commit()

            # Add files
            files = []
            data_to_insert = []

            for key in post_files:
                for filedata, filename in post_files[key]:
                    data_to_insert.append((filedata, filename, logid))

            cur.executemany(
                "INSERT INTO `file` (`blob`, `filename`, `log`) VALUES (?, ?, ?)",
                data_to_insert,
            )

            conn.commit()

            cur.execute(f"SELECT `id`, `filename` from `file` WHERE `log` = ?", (logid,))

            for row in cur:
                files.append({"id": row[0], "fileName": row[1]})

            data = {
                "id": logid,
                "itemId": int(post_data["itemId"][0]),
                "timestamp": post_data["timestamp"][0],
                "description": post_data["description"][0],
                "files": files,
            }

            conn.close()

            return True, "", data
        except Exception as e:
            logger.exception(e)
            return False, str(e), None
