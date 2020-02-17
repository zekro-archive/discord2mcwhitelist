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
        self._conn.execute(
            'CREATE TABLE IF NOT EXISTS `guilds` (' +
            '  `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,' +
            '  `guildId` VARCHAR(22),' +
            '  `adminRoleId` VARCHAR(32),' +
            '  `statusChannelId` VARCHAR(32),' +
            '  `statusMessageId` VARCHAR(32)' +
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

    def get_admin_role(self, guild_id: str) -> str:
        res = self._conn.execute(
            'SELECT `adminRoleId` from `guilds` WHERE ' +
            '`guildId` = ?;', (guild_id,))
        role = res.fetchone()
        return role[0] if role else None

    def set_admin_role(self, guild_id: str, role_id: str):
        res = self._conn.execute(
            'SELECT `guildId` from `guilds` WHERE ' +
            '`guildId` = ?;', (guild_id,))
        res_guild_id = res.fetchone()

        if res_guild_id is None:
            self._conn.execute(
                'INSERT INTO `guilds` (`guildId`, `adminRoleId`) VALUES ' +
                '(?, ?);', (guild_id, role_id))
        else:
            self._conn.execute(
                'UPDATE `guilds` SET `adminRoleId` = ? WHERE ' +
                '`guildId` = ?;', (role_id, guild_id))

        self._conn.commit()

    def get_status_channel(self, guild_id: str) -> str:
        res = self._conn.execute(
            'SELECT `statusChannelId` from `guilds` WHERE ' +
            '`guildId` = ?;', (guild_id,))
        chan = res.fetchone()
        return chan[0] if chan else None

    def set_status_channel(self, guild_id: str, channel_id: str):
        res = self._conn.execute(
            'SELECT `guildId` from `guilds` WHERE ' +
            '`guildId` = ?;', (guild_id,))
        res_guild_id = res.fetchone()

        if res_guild_id is None:
            self._conn.execute(
                'INSERT INTO `guilds` (`guildId`, `statusChannelId`) VALUES ' +
                '(?, ?);', (guild_id, channel_id))
        else:
            self._conn.execute(
                'UPDATE `guilds` SET `statusChannelId` = ? WHERE ' +
                '`guildId` = ?;', (channel_id, guild_id))

        self._conn.commit()

    def get_status_message(self, guild_id: str) -> str:
        res = self._conn.execute(
            'SELECT `statusMessageId` from `guilds` WHERE ' +
            '`guildId` = ?;', (guild_id,))
        msg = res.fetchone()
        return msg[0] if msg else None

    def set_status_message(self, guild_id: str, message_id: str):
        res = self._conn.execute(
            'SELECT `guildId` from `guilds` WHERE ' +
            '`guildId` = ?;', (guild_id,))
        res_guild_id = res.fetchone()

        if res_guild_id is None:
            self._conn.execute(
                'INSERT INTO `guilds` (`guildId`, `statusMessageId`) VALUES ' +
                '(?, ?);', (guild_id, message_id))
        else:
            self._conn.execute(
                'UPDATE `guilds` SET `statusMessageId` = ? WHERE ' +
                '`guildId` = ?;', (message_id, guild_id))

        self._conn.commit()
