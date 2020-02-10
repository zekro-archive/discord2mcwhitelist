import sqlite3
from sqlite3 import Connection


class SQLite:

    _conn: Connection

    def __init__(self, fileloc: str):
        self._conn = sqlite3.connect(fileloc)
        self._ensure_created()

    def close(self):
        self._conn.close()

    def _ensure_created(self):
        self._conn.execute(
            'CREATE TABLE IF NOT EXISTS `whitelist` (' +
            '  `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,' +
            '  `discordId` VARCHAR(22),' +
            '  `mcId` VARCHAR(32)' +
            ');')
        self._conn.commit()

    def get_whitelist(self) -> dict:
        res = self._conn.execute(
            'SELECT `discordId`, `mcId` FROM `whitelist`;')
        res_map = {}
        for e in res.fetchall():
            res_map[e[0]] = e[1]
        return res_map

    def get_whitelist_by_mc_id(self, mc_id: str) -> (str, str):
        res = self._conn.execute(
            'SELECT `discordId`, `mcId` FROM `whitelist` WHERE ' +
            '`mcId` = ?;', (mc_id,))
        row = res.fetchone()
        if row is None:
            return (None, None)
        print(row)
        return row

    def get_whitelist_by_discord_id(self, discord_id: str) -> (str, str):
        res = self._conn.execute(
            'SELECT `discordId`, `mcId` FROM `whitelist` WHERE ' +
            '`discordId` = ?;', (discord_id,))
        row = res.fetchone()
        if row is None:
            return (None, None)
        return row

    def set_witelist(self, discord_id: str, mc_id: str) -> str:
        dc_id, old_mc_id = self.get_whitelist_by_discord_id(discord_id)

        if dc_id is None:
            self._conn.execute(
                'INSERT INTO `whitelist` (`discordId`, `mcId`) VALUES ' +
                '(?, ?);', (discord_id, mc_id))
        else:
            self._conn.execute(
                'UPDATE `whitelist` SET `mcId` = ? WHERE ' +
                '`discordId` = ?;', (mc_id, discord_id))

        self._conn.commit()
        return old_mc_id

    def rem_witelist(self, ident: str):
        self._conn.execute(
            'DELETE FROM `whitelist` WHERE ' +
            '`discordId` = ? OR `mcId` = ?;', (ident, ident))
        self._conn.commit()
