CREATE DATABASE IF NOT EXISTS `equipment_record_fcs`;

USE `equipment_record_fcs`;

CREATE TABLE IF NOT EXISTS `inventoryitem`
(
    `id`           INTEGER PRIMARY KEY AUTO_INCREMENT,
    `invid`        VARCHAR(255) UNIQUE                                            NOT NULL,
    `category`     ENUM ('МОНОБЛОК', 'ПРИНТЕР', 'НОУТБУК', 'КОМПЬЮТЕР', 'МЕБЕЛЬ') NOT NULL,
    `display_name` VARCHAR(255)                                                   NOT NULL,
    `serial_num`   VARCHAR(255),
    `price`        DOUBLE,
    `available`    BOOLEAN
);

CREATE TABLE IF NOT EXISTS `inquiry`
(
    `id`             INTEGER PRIMARY KEY AUTO_INCREMENT,
    `inquirername`   VARCHAR(255)                       NOT NULL,
    `inquireremail`  VARCHAR(320)                       NOT NULL,
    `comment`        LONGTEXT                           NOT NULL,
    `status`         ENUM ('queued', 'finished', 'new') NOT NULL,
    `invid`          VARCHAR(255)                       NOT NULL,
    `itemname`       VARCHAR(255)                       NOT NULL,
    `inventory_item` INTEGER                            NOT NULL
);

CREATE INDEX `idx_inquiry__inventory_item` ON `inquiry` (`inventory_item`);

ALTER TABLE `inquiry`
    ADD CONSTRAINT `fk_inquiry__inventory_item` FOREIGN KEY (`inventory_item`) REFERENCES `inventoryitem` (`id`) ON DELETE CASCADE;

CREATE TABLE IF NOT EXISTS `user`
(
    `id`            INTEGER PRIMARY KEY AUTO_INCREMENT,
    `user_type`     ENUM ('ADMIN', 'READER') NOT NULL,
    `login`         VARCHAR(255) UNIQUE      NOT NULL,
    `password_hash` VARCHAR(255)             NOT NULL,
    `display_name`  VARCHAR(255)             NOT NULL
);

CREATE TABLE IF NOT EXISTS `log`
(
    `id`          INTEGER PRIMARY KEY AUTO_INCREMENT,
    `item_id`     INTEGER      NOT NULL,
    `timestamp`   DATETIME     NOT NULL,
    `description` VARCHAR(255) NOT NULL,
    `comment`     LONGTEXT     NOT NULL,
    `author`      INTEGER      NOT NULL
);

CREATE INDEX `idx_log__author` ON `log` (`author`);

CREATE INDEX `idx_log__item_id` ON `log` (`item_id`);

ALTER TABLE `log`
    ADD CONSTRAINT `fk_log__author` FOREIGN KEY (`author`) REFERENCES `user` (`id`) ON DELETE CASCADE;

ALTER TABLE `log`
    ADD CONSTRAINT `fk_log__item_id` FOREIGN KEY (`item_id`) REFERENCES `inventoryitem` (`id`) ON DELETE CASCADE;

CREATE TABLE IF NOT EXISTS `file`
(
    `id`       INTEGER PRIMARY KEY AUTO_INCREMENT,
    `blob`     BLOB         NOT NULL,
    `filename` VARCHAR(255) NOT NULL,
    `log`      INTEGER      NOT NULL
);

CREATE INDEX `idx_file__log` ON `file` (`log`);

ALTER TABLE `file`
    ADD CONSTRAINT `fk_file__log` FOREIGN KEY (`log`) REFERENCES `log` (`id`) ON DELETE CASCADE;

CREATE USER `erfcs_admin`@`localhost`
    IDENTIFIED BY 'admin';

CREATE USER `erfcs_reader`@`localhost`
    IDENTIFIED BY 'reader';


GRANT ALL PRIVILEGES
    ON `equipment_record_fcs`.*
    TO `erfcs_admin`@`localhost`;

GRANT SELECT
    ON `equipment_record_fcs`.file
    TO `erfcs_reader`@`localhost`;

GRANT SELECT
    ON `equipment_record_fcs`.inventoryitem
    TO `erfcs_reader`@`localhost`;

GRANT SELECT
    ON `equipment_record_fcs`.log
    TO `erfcs_reader`@`localhost`;

GRANT SELECT
    ON `equipment_record_fcs`.inquiry
    TO `erfcs_reader`@`localhost`;

# INSERT INTO `equipment_record_fcs`.`user` (user_type, login, password_hash, display_name)
# VALUES ('ADMIN', 'admin',
#         'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86',
#         'administrator');
#
# INSERT INTO `equipment_record_fcs`.`user` (user_type, login, password_hash, display_name)
# VALUES ('READER', 'accountant',
#         'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86',
#         'accountant');