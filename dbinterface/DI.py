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
    def get_item_list(search: str = "", offset: str = 0, categories: List[str] = []):
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
            if categories:
                query += (
                    "AND (inventoryitem.category IN ("
                    + ", ".join(["?"] * len(categories))
                    + ")) "
                )
                cur.execute(query, (search, search, search, search, *categories))
            else:
                cur.execute(query, (search, search, search, search))
            query += "LIMIT 20 OFFSET ?"

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
                "INNER JOIN `equipment_record_fcs`.`file` ON  log.item_id=? AND log.id = file.log",
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
                "SELECT inquiry.id, inquiry.inquirername, inquiry.inquirername, inquiry.comment, "
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
                    inquiry_data["inquirerName"],
                    inquiry_data["inquirerEmail"],
                    inquiry_data["comment"],
                    inquiry_data["status"],
                    int(inquiry_data["itemId"]),
                ),
            )
            conn.commit()
            cur.execute(
                "SELECT * FROM `equipment_record_fcs`.`inquiry` "
                "WHERE `inquirername`=? AND `inquireremail`=? AND "
                "`comment`=? AND `status`=? AND `inventory_item`=?",
                (
                    inquiry_data["inquirerName"],
                    inquiry_data["inquirerEmail"],
                    inquiry_data["comment"],
                    inquiry_data["status"],
                    int(inquiry_data["itemId"]),
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
            cur.execute(
                "INSERT INTO `equipment_record_fcs`.`inventoryitem` "
                "(invid, category, display_name, serial_num, price, available, description) "
                "VALUES (?, ?, ?, ?, ?, ?,?)",
                (
                    item_data["invid"],
                    item_data["category"],
                    item_data["displayName"],
                    item_data["serial_num"],
                    float(item_data["price"]),
                    item_data["available"],
                    item_data["description"],
                ),
            )
            conn.commit()
            cur.execute(
                "SELECT * FROM `equipment_record_fcs`.`inventoryitem` "
                "WHERE `invid`=? AND `category`=? AND "
                "`display_name`=? AND `description`=? AND `serial_num`=? AND `price`=? AND `available`=?",
                (
                    item_data["invid"],
                    item_data["category"],
                    item_data["displayName"],
                    item_data["description"],
                    item_data["serial_num"],
                    float(item_data["price"]),
                    item_data["available"],
                ),
            )
            data = {}
            for (
                id,
                invid,
                category,
                display_name,
                serial_num,
                price,
                available,
                description,
            ) in cur:
                data = {
                    "id": id,
                    "invid": invid,
                    "category": category,
                    "displayName": display_name,
                    "description": description,
                    "serial_num": serial_num,
                    "price": price,
                    "available": available,
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
                    item_data["invid"],
                    item_data["category"],
                    item_data["displayName"],
                    item_data["serial_num"],
                    float(item_data["price"]),
                    item_data["available"],
                    item_data["description"],
                    item_data["id"],
                ),
            )

            conn.commit()
            if cur.rowcount == 0:
                return False, "couldn't find the specifed item", {}
            data = {
                "id": item_data["id"],
                "invid": item_data["invid"],
                "category": item_data["category"],
                "displayName": item_data["displayName"],
                "description": item_data["description"],
                "serial_num": item_data["serial_num"],
                "price": item_data["price"],
                "available": item_data["available"],
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
                (int(updated_data["itemId"]),),
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
            cur.execute(
                "SELECT id from `equipment_record_fcs`.`log` WHERE item_id=? AND timestamp=? AND description=?",
                (
                    int(post_data["itemId"][0]),
                    post_data["timestamp"][0],
                    post_data["description"][0],
                ),
            )
            logid = -1
            for (id,) in cur:
                logid = id
            if logid < -1:
                return False, "failed to add", {}
            filename1 = post_files["excel"][0][1]
            filename2 = post_files["word"][0][1]
            conn.commit()
            entries_of_a_filename = -1
            while entries_of_a_filename != 0:
                cur.execute(
                    "SELECT COUNT(filename) "
                    "FROM `equipment_record_fcs`.`file`"
                    "WHERE filename=?",
                    (filename1,),
                )
                (entries_of_a_filename,) = cur.fetchone()
                logger.debug(entries_of_a_filename)
                if entries_of_a_filename != 0:
                    filename1 += f'_{post_data["timestamp"][0]}'
            insert_file_query = (
                "INSERT INTO `equipment_record_fcs`.`file` "
                "(`blob`, filename, log) "
                "VALUES (?, ?, ?)"
            )

            cur.execute(
                insert_file_query, (post_files["excel"][0][0], filename1, logid)
            )
            conn.commit()
            entries_of_a_filename = -1
            while entries_of_a_filename != 0:
                cur.execute(
                    "SELECT COUNT(filename) "
                    "FROM `equipment_record_fcs`.`file`"
                    "WHERE filename=?",
                    (filename2,),
                )
                (entries_of_a_filename,) = cur.fetchone()
                if entries_of_a_filename != 0:
                    filename2 += f'_{post_data["timestamp"][0]}'
            cur.execute(insert_file_query, (post_files["word"][0][0], filename2, logid))
            conn.commit()
            fileid1, fileid2 = -1, -1
            cur.execute(
                "SELECT id FROM `equipment_record_fcs`.`file`" "WHERE filename=?",
                (filename1,),
            )
            for (id,) in cur:
                fileid1 = id
            cur.execute(
                "SELECT id FROM `equipment_record_fcs`.`file`" "WHERE filename=?",
                (filename2,),
            )
            for (id,) in cur:
                fileid2 = id

            if fileid1 < -1 or fileid2 < -1:
                return False, "failed to add", {}

            cur.execute(
                "INSERT INTO `equipment_record_fcs`.`file`"
                "(`blob`, filename, log) "
                "VALUES (?, ?, ?), (?, ?, ?)",
                (
                    post_files["excel"][0][0],
                    filename1,
                    logid,
                    post_files["word"][0][0],
                    filename2,
                    logid,
                ),
            )

            data = {
                "id": logid,
                "itemId": int(post_data["itemId"][0]),
                "timestamp": post_data["timestamp"][0],
                "description": post_data["description"][0],
                "excel_file": {"id": fileid1, "fileName": filename1},
                "word_file": {"id": fileid2, "fileName": filename2},
            }

            conn.close()

            return True, "", data
        except Exception as e:
            logger.exception(e)
            return False, str(e), None
