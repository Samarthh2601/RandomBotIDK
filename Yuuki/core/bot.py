import logging
import datetime
import hikari
import lightbulb

import aiohttp

from ..utils import APP_KEY, OWNER_IDS, EXTENSION_PATH
from ..database import MessageDB, UserDB

class Yuuki(lightbulb.BotApp):
    def __init__(self) -> None:
        super().__init__(token=APP_KEY, owner_ids=OWNER_IDS, intents=hikari.Intents.ALL, help_slash_command=True)
        self.load_extensions_from(EXTENSION_PATH)
        self.event_manager.subscribe(hikari.StartingEvent, self.setup)

    async def setup(self, event: hikari.StartingEvent) -> None:
        self._boot = datetime.datetime.utcnow()
        self.message_db = MessageDB()
        self.user_db = UserDB()
        self.logger = logging.getLogger()
        self.http = aiohttp.ClientSession()
        await self.message_db.setup()
        await self.user_db.setup()
    
    @property
    def uptime(self) -> str:
        return str(datetime.datetime.utcnow() - self._boot)
    
    async def getch_message(self, message_id: int, channel_id: int) -> hikari.Message:
        return self.cache.get_message(message_id) or await self.rest.fetch_message(channel_id, message_id)
        
    async def getch_member(self, guild_id: int, member_id: int) -> hikari.Member:
        return self.cache.get_member(guild_id, member_id) or await self.rest.fetch_member(guild_id, member_id)
    
    async def getch_user(self, user_id: int) -> hikari.User:
        return self.cache.get_user(user_id) or await self.rest.fetch_user(user_id)
    
    async def getch_guild(self, guild_id: int) -> hikari.Guild:
        return self.cache.get_guild(guild_id) or await self.rest.fetch_guild(guild_id)
    
    async def getch_emoji(self, emoji_id: int, guild_id: int) -> hikari.Emoji:
        return self.cache.get_emoji(emoji_id) or await self.rest.fetch_emoji(guild_id, emoji_id)
    
    async def getch_channel(self, channel_id: int) -> hikari.GuildChannel:
        return self.cache.get_guild_channel(channel_id) or await self.rest.fetch_channel(channel_id)