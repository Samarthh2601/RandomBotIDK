import hikari
import lightbulb
from ..core import Yuuki
from ..utils import get_id

class Track(lightbulb.Plugin):
    def __init__(self) -> None:
        super().__init__("Track Messages and Users!", "Track messages and users for any change!")
        self.bot: Yuuki

track = Track()

@track.command
@lightbulb.option(name="id_or_link", description="The ID or the link of the message!", type=str, required=True)
@lightbulb.option(name="message_channel", description="The channel the message is in!", type=hikari.TextableGuildChannel, required=True)
@lightbulb.command(name="track_message", description="Track a message for any changes!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def track_message(ctx: lightbulb.SlashContext) -> None:
    message_id = get_id(ctx)
    
    if message_id is None:
        return await ctx.respond("Invalid Message ID/Link was given!")

    channel: hikari.TextableGuildChannel = ctx._options.get("message_channel")
    message = await track.bot.getch_message(message_id, channel.id)
    
    s = await track.bot.message_db.create(ctx.author.id, channel.id, message_id, ctx.guild_id)

    if s is False:
        return await ctx.respond("You have already reached the maximum amount of message trackers!")

    await ctx.respond(f"Now tracking [this]({message.make_link(ctx.guild_id)}) message!")


@track.command
@lightbulb.option(name="user", description="The user to track!", type=hikari.Member, required=True)
@lightbulb.command(name="track_user", description="Track a User for any changes!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def track_user(ctx: lightbulb.SlashContext) -> None:
    member: hikari.Member = ctx._options.get("user")
    s = await track.bot.user_db.create(ctx.author.id, member.id)
    if s is False:
        return await ctx.respond("You have already reached the maximum amount of user trackers!")        
    return await ctx.respond(f"Now tracking changes for {member.mention}")

@track.command
@lightbulb.option(name="user", description="The user to check the tracked messages of!", type=hikari.Member, required=False)
@lightbulb.command(name="messages_on_track", description="The messages that are currently being tracked!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def current_messages_on_track(ctx: lightbulb.SlashContext) -> None:
    _user: hikari.Member = ctx._options.get("user") or ctx.author
    messages = await track.bot.message_db.read_user(_user.id)
    if messages is None:
        return await ctx.respond("No messages are being tracked currently!")
    embed = hikari.Embed(title="Current Tracking Messages", description="\n- ".join([f"https://discord.com/channels/{message.guild_id}/{message.channel_id}/{message.message_id}" for message in messages])).set_footer(_user.username, icon=_user.display_avatar_url)
    await ctx.respond(embed=embed)

@track.command
@lightbulb.option(name="user", description="The user to check the tracked users of!", type=hikari.Member, required=False)
@lightbulb.command(name="users_on_track", description="The users that are currently being tracked!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def current_users_on_track(ctx: lightbulb.SlashContext) -> None:
    member: hikari.Member = ctx._options.get("user") or ctx.author
    users = await track.bot.user_db.read_user(member.id)
    if users is None:
        return await ctx.respond("No users are being tracked currently!")
    embed = hikari.Embed(title="Current tracking users!", description="\n- ".join(f"<@{user.target_id}>" for user in users)).set_footer(member.username, icon=member.display_avatar_url)
    await ctx.respond(embed=embed)

@track.command
@lightbulb.option(name="id_or_link", description="The ID or the link of the message!", type=str, required=True)
@lightbulb.command(name="untrack_message", description="Untrack a message!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def untrack_message(ctx: lightbulb.SlashContext) -> None:
    message_id = get_id(ctx)

    if message_id is None:
        return await ctx.respond("Invalid Message ID/Link was given!")

    message = await track.bot.message_db.remove(ctx.author.id, message_id)
    if message is False:
        return await ctx.respond("Could not find any tracked messages with that link/ID!")
    await ctx.respond(f"Successfully untracked [this](https://discord.com/channels/{message.guild_id}/{message.channel_id}/{message.message_id}) message!")

@track.command
@lightbulb.option(name="user", description="The user to untrack!", type=hikari.Member, required=True)
@lightbulb.command(name="untrack_user", description="Untrack a user!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def untrack_user(ctx: lightbulb.SlashContext) -> None:
    member: hikari.Member = ctx._options.get("user")

    info = await track.bot.user_db.remove(ctx.author.id, member.id)

    if info is False:
        return await ctx.respond(f"{member.mention} isn't being tracked!")

    await ctx.respond(f"Successfully untracked <@{info.target_id}>")

def load(_bot: Yuuki):
    _bot.add_plugin(track)