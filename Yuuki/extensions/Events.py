import lightbulb
import hikari
from ..core import Yuuki
from ..utils import get_attachment, find_content, send_message, COLOURS

class Events(lightbulb.Plugin):
    def __init__(self) -> None:
        super().__init__("Events!", "Event manager!")
        self.bot: Yuuki

events = Events()

@events.listener(hikari.MessageDeleteEvent)
async def msg_delete(event: hikari.MessageDeleteEvent) -> None:
    s = await events.bot.message_db.read_message(event.message_id)
    if not s: return
    attachment = await get_attachment(event.old_message)

    embed = hikari.Embed(title="Message deleted!", description="A message you had been tracking has been deleted!", colour=COLOURS.amber).add_field("Message content", find_content(event)).add_field("Message Author", event.old_message.author if event.old_message else "Could not find author")

    if event.old_message is not None:
        embed.set_thumbnail(event.old_message.author.display_avatar_url)

    if attachment is not None:
        embed.set_image(attachment)

    await send_message(events.bot, s, embed)
    deletions = [await events.bot.message_db.remove(record.user_id, record.message_id) for record in s]
    events.bot.logger.info("Deleted %r record(s) due to message deletion", len(deletions))

@events.listener(hikari.GuildMessageUpdateEvent)
async def message_update(event: hikari.GuildMessageUpdateEvent) -> None:
    s = await events.bot.message_db.read_message(event.message_id)
    if not s: return
    attachment = await get_attachment(event.message)
    embed = hikari.Embed(title="Message Edited!", description="A message you had been tracking has been edited!", colour=COLOURS.zaffre).add_field("Author", event.message.author.username).add_field("Link", f"[Go to message]({event.message.make_link(event.message.guild_id)})")

    if event.message is not None:
        embed.set_thumbnail(event.message.author.display_avatar_url)

    if attachment is not None:
        embed.set_image(attachment)

    await send_message(events.bot, s, embed)

@events.listener(hikari.GuildReactionAddEvent)
async def reaction_add(event: hikari.GuildReactionAddEvent) -> None:
    s = await events.bot.message_db.read_message(event.message_id)
    if not s: return
    if event.emoji_id is None: emoji = event.emoji_name
    else: emoji = str(await events.bot.getch_emoji(event.emoji_id, event.guild_id))
    guild = await events.bot.getch_guild(event.guild_id)
    embed = hikari.Embed(title="Reaction Added!", description="A message you had been tracking has been reacted to!", colour=COLOURS.jasper).add_field("Server", guild.name).add_field("Channel", f"<#{event.channel_id}>").add_field("Emoji", emoji).add_field("Message", f"[Go to message](https://discord.com/channels/{event.guild_id}/{event.channel_id}/{event.message_id})").set_thumbnail(guild.icon_url if guild.icon_url else None)

    await send_message(events.bot, s, embed)

@events.listener(hikari.GuildReactionDeleteEvent)
async def reaction_remove(event: hikari.GuildReactionDeleteEvent) -> None:
    s = await events.bot.message_db.read_message(event.message_id)
    if not s: return
    guild = await events.bot.getch_guild(event.guild_id)
    if event.emoji_id is None: emoji = event.emoji_name
    else: emoji = str(await events.bot.getch_emoji(event.emoji_id, event.guild_id))
    embed = hikari.Embed(title="Reaction removed!", description="A message you had been tracking has been un-reacted to!", colour=0x03fccf).add_field("Server", guild.name).add_field("Channel", f"<#{event.channel_id}>").add_field("Emoji", emoji if emoji else event.emoji_name).add_field(f"Message", f"[Go to message](https://discord.com/channels/{event.guild_id}/{event.channel_id}/{event.message_id})").set_thumbnail(guild.icon_url if guild.icon_url else None)

    await send_message(events.bot, s, embed)

@events.listener(hikari.MemberDeleteEvent)
async def member_remove(event: hikari.MemberDeleteEvent) -> None:
    s = await events.bot.user_db.read_target(event.user_id)
    if not s: return
    guild = await events.bot.getch_guild(event.guild_id)
    embed = hikari.Embed(title="User Removed!", description="A user you had been tracking has been removed from a server!", colour=COLOURS.ash_grey).add_field("Server", guild.name).add_field("User", str(event.user)).set_thumbnail(event.user.default_avatar_url if event.user.default_avatar_url else None)

    await send_message(events.bot, s, embed)


@events.listener(hikari.MemberCreateEvent)
async def member_create(event: hikari.MemberCreateEvent) -> None:
    s = await events.bot.user_db.read_target(event.user_id)
    if not s: return
    guild = await events.bot.getch_guild(event.guild_id)

    embed = hikari.Embed(title="User Joined!", description="A user you had been tracking has joined a new server!", colour=COLOURS.cornflower_blue).add_field("Server", guild.name).add_field("User", str(event.user)).set_thumbnail(event.member.display_avatar_url if event.member.display_avatar_url else None)

    await send_message(events.bot, s, embed)

@events.listener(hikari.MemberUpdateEvent)
async def member_update(event: hikari.MemberUpdateEvent) -> None:
    s = await events.bot.user_db.read_target(event.user_id)
    if not s: return
    guild = await events.bot.getch_guild(event.guild_id)

    embed = hikari.Embed(title="User Updated!", description="A user you had been tracking has just been updated in a server!", colour=COLOURS.old_lavender).add_field("Server", guild.name).add_field("User", str(event.user)).set_thumbnail(event.member.display_avatar_url if event.member.display_avatar_url else None)

    await send_message(events.bot, s, embed)

def load(bot: Yuuki):
    bot.add_plugin(events)