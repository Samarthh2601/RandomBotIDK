from dataclasses import dataclass
from typing import Union
import hikari
import lightbulb
from typing import Any
import aiohttp

from .colours import Colours
from .info import NEWS_KEY

EXTENSION_PATH = "./Yuuki/extensions"
COLOURS = Colours()

@dataclass
class Record:
    message_id: int
    user_id: int
    guild_id: int
    channel_id: int=None

@dataclass 
class UserRecord:
    user_id: int
    target_id: int

def find_content(event: hikari.MessageDeleteEvent, /) -> str:
    if event.old_message is None:
        content = "*Could not find any content*"
    
    elif event.old_message.content is None and event.old_message.attachments:
        content = "Contains attachment..."

    elif event.old_message.embeds:
        content = event.old_message.embeds[0].title or event.old_message.embeds[0].description

    else:
        content = event.old_message.content if event.old_message.content is not None and not event.old_message.content.isspace() else "*Could not find any content*"
        

    return content

async def get_attachment(message: hikari.Message, /) -> Union[None, bytes, hikari.Bytes]:
    if not message: return None
    if not message.attachments: return None
    return await message.attachments[0].read() if message.attachments[0].extension in ("png", "jpg", "jpeg") else None


def get_id(ctx: lightbulb.SlashContext, /) -> Union[None, str]:
    _content: str = ctx._options.get("id_or_link")
    if len(_content) == 18 and _content.isdigit(): message_id = _content

    elif len(_content) == 85 and not _content.isdigit() and _content.startswith("https://discord.com/channels/"): message_id = _content.split("/")[-1]

    else:
        return None
    
    return message_id

def get_stripped_content(message: hikari.Message, /) -> str:
    if not message.content and message.embeds or not message.content and message.attachments:
        initial_message_chars = "Contains Embeds/Images/etc..."
    else:
        message_length = len(message.content)
        if message_length > 10: initial_message_chars = message.content[0:10]
        elif message_length <= 10 and message_length >= 5: initial_message_chars = message.content[0:8]
        elif message_length <= 5: initial_message_chars = message.content[0:5]

    return initial_message_chars

async def send_message(bot: Any, all_records: Union[Record, UserRecord], embed: hikari.Embed):
    for record in all_records:
        try: await (await bot.getch_user(record.user_id)).send(embed=embed)
        except (hikari.ForbiddenError, hikari.NotFoundError, hikari.BadRequestError): pass

LANGUAGES = ['afrikaans', 'albanian', 'amharic', 'arabic', 'armenian', 'azerbaijani', 'basque', 'belarusian', 'bengali', 'bosnian', 'bulgarian', 'catalan', 'cebuano', 'chichewa', 'chinese (simplified)', 'chinese (traditional)', 'corsican', 'croatian', 'czech', 'danish', 'dutch', 'english', 'esperanto', 'estonian', 'filipino', 'finnish', 'french', 'frisian', 'galician', 'georgian', 'german', 'greek', 'gujarati', 'haitian creole', 'hausa', 'hawaiian', 'hebrew', 'hindi', 'hmong', 'hungarian', 'icelandic', 'igbo', 'indonesian', 'irish', 'italian', 'japanese', 'javanese', 'kannada', 'kazakh', 'khmer', 'kinyarwanda', 'korean', 'kurdish', 'kyrgyz', 'lao', 'latin', 'latvian', 'lithuanian', 'luxembourgish', 'macedonian', 'malagasy', 'malay', 'malayalam', 'maltese', 'maori', 'marathi', 'mongolian', 'myanmar', 'nepali', 'norwegian', 'odia', 'pashto', 'persian', 'polish', 'portuguese', 'punjabi', 'romanian', 'russian', 'samoan', 'scots gaelic', 'serbian', 'sesotho', 'shona', 'sindhi', 'sinhala', 'slovak', 'slovenian', 'somali', 'spanish', 'sundanese', 'swahili', 'swedish', 'tajik', 'tamil', 'tatar', 'telugu', 'thai', 'turkish', 'turkmen', 'ukrainian', 'urdu', 'uyghur', 'uzbek', 'vietnamese', 'welsh', 'xhosa', 'yiddish', 'yoruba', 'zulu']

async def get_news(*, req_client: aiohttp.ClientSession, query: str) -> dict[str]:
    resp = await req_client.get(f'https://newsapi.org/v2/everything?q={query}&pageSize=1&sortBy=popularity&apiKey={NEWS_KEY}')
    if resp.status != 200:
        return {"error": "Could not find news!"}
    content = await resp.json()
    return {"author": content["articles"][0]["author"],"content": content["articles"][0]["content"],"description": content["articles"][0]["description"],"title": content["articles"][0]["title"],"url": content["articles"][0]["url"],"image": content["articles"][0]["urlToImage"],}