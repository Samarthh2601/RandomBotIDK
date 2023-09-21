import asyncio
import lightbulb
import hikari

from ..core import Yuuki
from ..utils import COLOURS, LANGUAGES, get_id, get_stripped_content
from deep_translator import GoogleTranslator


class General(lightbulb.Plugin):
    def __init__(self) -> None:
        super().__init__("General", "General commands")
        self.bot: Yuuki
        self.translator = GoogleTranslator()

gen = General()

@gen.command
@lightbulb.option(name="language", description="The language to convert the text to!", required=True, autocomplete=True, type=str)
@lightbulb.option(name="source_language", description="The language to convert the text from!", required=True, autocomplete=True, type=str)
@lightbulb.option(name="text", description="The text to translate!", required=True, type=str)
@lightbulb.command(name="translate", description="Translate text to another language!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def translate_text(ctx: lightbulb.SlashContext) -> None:
    language = ctx._options.get("language")
    loop = asyncio.get_event_loop_policy().get_event_loop()
    gen.translator.target = language
    def _() -> None:
        return gen.translator.translate(ctx._options.get("text"))
    res = await loop.run_in_executor(None, _)
    
    embed = hikari.Embed(title="Translation Success!", description=f"**English** to **{language}**", colour=COLOURS.american_rose).add_field("Translated text", res[:1000])
    await ctx.respond(embed=embed)

@translate_text.autocomplete("language", "source_language")
async def autocomplete_language(option: hikari.AutocompleteInteractionOption, interaction: hikari.AutocompleteInteraction) -> None:
    return [lang for lang in LANGUAGES if option.value in lang]

@gen.command
@lightbulb.command(name="supported_languages", description="Get all the supported languages for /translate", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def supported_langs(ctx: lightbulb.SlashContext) -> None:
    embed = hikari.Embed(title="Supported Languages", description=", ".join(LANGUAGES), colour=COLOURS.bulgarian_rose)
    await ctx.respond(embed=embed)

@gen.command
@lightbulb.option(name="member", description="The member to send this message to!", type=hikari.Member, required=True)
@lightbulb.option(name="message", description="The content to send!", type=str, required=True)
@lightbulb.command(name="send", description="Send A Message To Another Member!", ephemeral=True, auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def message(ctx: lightbulb.SlashContext) -> None:
    member: hikari.Member = ctx._options.get("member")
    message = ctx._options.get("message")
    if ctx.author == member:
        return await ctx.respond("You cannot send a message to yourself!")

    if len(message) > 1000:
        return await ctx.respond("Message Content Limit crossed!")

    embed= hikari.Embed(title=f"You have received a message from {ctx.author.username}!", description=message, color=ctx.author.accent_color).set_thumbnail(ctx.author.display_avatar_url)
    try:
        await member.send(embed=embed)
        await ctx.respond(f"Successfully Messaged {member.mention}!")
    except hikari.ForbiddenError:
        return await ctx.respond(f"{member.mention}'s DMs are disabled!")

@gen.command
@lightbulb.option(name="member", description="The Member to get the avatar of!", type=hikari.Member, required=False)
@lightbulb.command(name="avatar", description="Get your avatar or of a Member's!", ephemeral=True, auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_avatar(ctx: lightbulb.SlashContext) -> None:
    member: hikari.Member = ctx._options.get("member") or ctx.author
    embed = hikari.Embed(color=member.accent_color).set_image(member.display_avatar_url)
    await ctx.respond(embed=embed)

@gen.command
@lightbulb.option(name="member", description="The Member to get information of!", type=hikari.Member, required=False)
@lightbulb.command(name="profile", description="Get Information about a Member!", ephemeral=True, auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_user_info(ctx: lightbulb.SlashContext) -> None:
    member: hikari.Member = ctx._options.get("member") or ctx.member
    presence = member.get_presence()
    if presence:
        if presence.activities: activities = [activity.name for activity in presence.activities]
        else: activities = "No Activity"
    
    nickname = member.nickname
    if not nickname:
        nickname = "No Nick Name"

    embed = hikari.Embed(color=member.accent_color).set_image(member.display_avatar_url).add_field("Username", member, inline=True).add_field("Name", member.username, inline=True).add_field("Tagline", member.discriminator, inline=True).add_field("Nickname", nickname, inline=True).add_field("Discord ID", member.id, inline=True).add_field("Colour", member.get_top_role().color, inline=True).add_field("Number of Roles", len(member.role_ids)-1, inline=True).add_field("Server Join", member.joined_at.strftime("%Y-%m-%d"), inline=True).add_field("Account Creation", member.created_at.strftime("%Y-%m-%d"), inline=True).add_field("Status", presence.visible_status, inline=True).add_field("Activities", activities, inline=True).add_field("Avatar URL", f"[{member.username}'s avatar URL]({member.display_avatar_url})", inline=True)
    await ctx.respond(embed=embed)

@gen.command
@lightbulb.option(name="id_or_link", description="Enter the Message link or ID", required=True)
@lightbulb.command(name="bookmark", description="Get a link to the message straight to your DMs! Run the command in the same channel as the message!", ephemeral=True, auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def bm_mes(ctx: lightbulb.SlashContext) -> None:
    message_id = get_id(ctx)
    if message_id is None:
        return await ctx.respond("Invalid Message ID/Link was given!")

    message = await gen.bot.getch_message(message_id, ctx.channel_id)
    message_channel = await gen.bot.getch_channel(message.channel_id)    

    embed = hikari.Embed(title="Message Bookmark", description=f"{get_stripped_content(message)}...", color=ctx.author.accent_colour).set_thumbnail(ctx.author.display_avatar_url).add_field("Server", ctx.get_guild().name, inline=True).add_field("Message author", message.author, inline=True).add_field("Message Channel", message_channel.name, inline=True).add_field("Original Message", f"[See Original Message]({message.make_link(ctx.guild_id)})")
    try:
        await ctx.author.send(embed=embed)
        await ctx.respond("Successfully sent you the bookmark!")
    except hikari.ForbiddenError:
        await ctx.respond("Your DMs are disabled! Enable your DMs to get a link!")

@gen.command
@lightbulb.option(name="text", description="The text to reply with!", required=True, type=str)
@lightbulb.option(name="id_or_link", description="Enter the Message link or ID to reply to!", required=True)
@lightbulb.option(name="member", description="This will default to the specified message's author if not given", required=False, type=hikari.Member)
@lightbulb.command(name="reply", description="Reply to a Member's message!", ephemeral=True, auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def reply_msg(ctx: lightbulb.SlashContext) -> None:
    if len(ctx._options.get("text")) > 500:
        return await ctx.respond("The text should be under 500 characters!")

    message_id = get_id(ctx)

    if message_id is None:
        return await ctx.respond("Invalid Message ID/Link was given!")

    message = await gen.bot.getch_message(message_id, ctx.channel_id)
    message_channel = await gen.bot.getch_channel(message.channel_id)    
    
    _member: hikari.Member = ctx._options.get("member") or message.author


    embed = hikari.Embed(title=f"Replying on behalf of {ctx.author}", description=ctx._options.get("text"), color=ctx.author.accent_colour).set_thumbnail(ctx.author.display_avatar_url).add_field("Message ref", f"{get_stripped_content(message)}...", inline=True).add_field("Server", ctx.get_guild().name, inline=True).add_field("Message author", message.author, inline=True).add_field("Message Channel", message_channel.name, inline=True).add_field("Original Message", f"[See Original Message]({message.make_link(ctx.guild_id)})")
    try:
        await _member.send(embed=embed)
        await ctx.respond(f"Successfully replied to {_member}!")
    except hikari.ForbiddenError:
        await ctx.respond("Could not message that user!")


def load(bot: Yuuki) -> None:
    bot.add_plugin(gen)