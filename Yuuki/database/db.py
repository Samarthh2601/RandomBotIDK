import aiosqlite
from typing import Union

from ..utils import Record, UserRecord

class MessageDB:
    conn: aiosqlite.Connection
    cur: aiosqlite.Cursor

    async def setup(self) -> None:
        self.conn = await aiosqlite.connect("./Yuuki/database/messages.db")
        self.cur = await self.conn.cursor()
        await self.cur.execute("CREATE TABLE IF NOT EXISTS messages(user_id INTEGER, channel_id INTEGER, message_id INTEGER, guild_id INTEGER)")
        await self.conn.commit()

    async def read_user_message(self, user_id: int, message_id: int) -> Union[None, Record]:
        record = await (await self.cur.execute("SELECT * FROM messages WHERE user_id = ? AND message_id = ?", (user_id, message_id,))).fetchone()
        if not record: return None
        return Record(record[2], record[0], record[3], record[1])

    async def read_message(self, message_id: int) -> Union[None, list[Record, Record, Record]]:
        record = await (await self.cur.execute("SELECT * FROM messages WHERE message_id = ?", (message_id,))).fetchall()
        if not record: return None
        return [Record(record[2], record[0], record[3], record[1]) for record in record]

    async def read_user(self, user_id: int) -> Union[None, list[Record, Record, Record]]:
        record = await (await self.cur.execute("SELECT * FROM messages WHERE user_id = ?", (user_id,))).fetchall()
        if not record: return None
        return [Record(record[2], record[0], record[3], record[1]) for record in record]

    async def create(self, user_id: int, channel_id: int, message_id: int, guild_id: int) -> Union[bool, Record]:
        _check = await self.read_user(user_id)
        if _check is not None:
            if len(_check) >= 3:
                return False
        await self.cur.execute("INSERT INTO messages(user_id, channel_id, message_id, guild_id) VALUES(?, ?, ?, ?)", (user_id, channel_id, message_id, guild_id,))
        await self.conn.commit()
        return Record(message_id, user_id, guild_id, channel_id)
    
    async def remove(self, user_id: int, message_id: int) -> Union[bool, Record]:
        _check = await self.read_user_message(user_id, message_id)
        if _check is None:
            return False
        await self.cur.execute("DELETE FROM messages WHERE user_id = ? AND message_id = ?", (_check.user_id, _check.message_id,))
        await self.conn.commit()
        return Record(_check.message_id, _check.user_id, _check.guild_id, _check.channel_id)

class UserDB:
    conn: aiosqlite.Connection
    cur: aiosqlite.Cursor

    async def setup(self) -> None:
        self.conn = await aiosqlite.connect("./Yuuki/database/users.db")
        self.cur = await self.conn.cursor()
        await self.cur.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER, target_id INTEGER)")
        await self.conn.commit()

    async def read_target(self, target_id: int) -> Union[None, list[UserRecord, UserRecord, UserRecord]]:
        record = await (await self.cur.execute("SELECT * FROM users WHERE target_id = ?", (target_id,))).fetchall()
        if not record: return None
        return [UserRecord(record[0], record[1]) for record in record]

    async def read_user(self, user_id: int) -> Union[None, list[UserRecord, UserRecord, UserRecord]]:
        record = await (await self.cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))).fetchall()
        if not record: return None
        return [UserRecord(record[0], record[1]) for record in record]
    
    async def read(self, user_id: int, target_id: int) -> Union[None, UserRecord]:
        record = await (await self.cur.execute("SELECT * FROM users WHERE user_id = ? AND target_id = ?", (user_id, target_id,))).fetchone()
        if not record:
            return None
        return UserRecord(record[0], record[1])

    async def create(self, user_id: int, target_id: int) -> Union[bool, UserRecord]:
        _check = await self.read_user(user_id)
        if _check is not None:
            if len(_check) >= 3:
                return False
        await self.cur.execute("INSERT INTO users(user_id, target_id) VALUES(?, ?)", (user_id, target_id))
        await self.conn.commit()
        return UserRecord(user_id, target_id)
    
    async def remove(self, user_id: int, target_id: int) -> Union[bool, UserRecord]:
        _check = await self.read(user_id, target_id)
        if _check is None:
                return False
        await self.cur.execute("DELETE FROM users WHERE user_id = ? AND target_id = ?", (_check.user_id, _check.target_id,))
        await self.conn.commit()
        return UserRecord(user_id, target_id)