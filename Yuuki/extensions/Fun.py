import hikari
import lightbulb

from ..core import Yuuki
from ..utils import COLOURS, get_news, MOVIE_KEY
import jokeapi

class Fun(lightbulb.Plugin):
    def __init__(self) -> None:
        super().__init__("Fun", "Fun utility commands!")
        self.bot: Yuuki
    
fun = Fun()

@fun.command
@lightbulb.option(name="query", description="The subject to search for!", type=str, required=True)
@lightbulb.command(name="news", description="Get news about a topic!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def news(ctx: lightbulb.SlashContext) -> None:
    response = await get_news(query=ctx._options.get("query"), req_client=fun.bot.http)
    news_error = response.get("error")
    if news_error:
        return await ctx.respond(news_error)

    embed = hikari.Embed(title=response.get("title"), description=response.get("description"), colour=ctx.author.accent_colour).add_field("** **", response.get("content")).add_field("Author", response.get("author")).add_field("Article", f"You can get the article [here]({response.get('url')})!").set_thumbnail(response.get("image"))
    return await ctx.respond(embed=embed)

@fun.command
@lightbulb.option(name="word", description="The word to search!", type=str, required=True)
@lightbulb.command(name="def", description="Get the meaning of a word!", ephemeral=True, auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_meaning(ctx: lightbulb.SlashContext):
    word_to_search = ctx._options.get("word")
    resp = await fun.bot.http.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word_to_search}")
    if resp.status != 200:
        return await ctx.respond("Could not find that word!")
    data = await resp.json()[0]
    embed = hikari.Embed(title=data['word'], description=f"{data['phonetics'][1]['text']}\nYou can listen to the pronunciation [here]({data['phonetics'][0]['audio']}) (if applicable)", colour=ctx.author.accent_color).add_field("Part of Speech", data['meanings'][0]['partOfSpeech']).add_field("More Links", "\n".join(data['sourceUrls'])).add_field("Definitions", "\n- ".join([definit['definition'] for definit in data['meanings'][0]['definitions']]))
    await ctx.respond(embed=embed)

@fun.command
@lightbulb.command(name="insult", description="Send something insulting!", ephemeral=True, auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_insult(ctx: lightbulb.SlashContext):
    resp = await fun.bot.http.get("https://evilinsult.com/generate_insult.php?lang=en&type=json")
    if resp.status != 200:
        return await ctx.respond("Could not find an insult!")
    data = await resp.json()
    return await ctx.respond(f"**{data['insult']}**")

@fun.command
@lightbulb.command(name="quote", description="Get a quote!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_quote(ctx: lightbulb.SlashContext):
    resp = await fun.bot.http.get("https://zenquotes.io/api/random")
    if resp.status != 200:
        return await ctx.respond("Could not get a quote!")
    data = await resp.json()[0]
    await ctx.respond(f"**{data['q']}** - *{data['a']}*")

@fun.command
@lightbulb.option(name="movie", description="The Movie name!", type=str, required=True)
@lightbulb.command(name="movie", description="Get information about a movie!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_movie_data(ctx: lightbulb.SlashContext):
    movie = ctx._options.get("movie")
    res = await fun.bot.http.get(f"http://www.omdbapi.com/?t={movie.title()}&plot=full&apikey=" + MOVIE_KEY)
    if res.status != 200:
        return await ctx.respond("Could not find that movie!")
    content = await res.json()
    embed = hikari.Embed(title=content['Title']).add_field(name="Released", value=content['Released']).add_field(name="Duration", value=content['Runtime']).add_field(name="Genre", value=content['Genre']).add_field(name="Rated", value=content['Rated']).add_field(name="Directed By", value=content['Director']).add_field(name="Casts", value=content['Actors']).set_thumbnail(content['Poster'])
    
    embed.add_field(name="Plot", value=f"{content['Plot'][:200]}...", inline=False).add_field(name="Country", value=content['Country']).add_field(name="Awards", value=content['Awards']).add_field(name="IMDB Rating", value=content['imdbRating']).add_field(name="Box Office Earnings", value=content['BoxOffice']).add_field(name="IMDB Upvotes", value=content['imdbVotes'])
    for rate in content['Ratings']:
        embed.add_field(name=rate['Source'], value=rate['Value'])
    await ctx.respond(embed=embed)
    
@fun.command
@lightbulb.command(name="joke", description="Get a random joke!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_joke(ctx: lightbulb.SlashContext):
    j = await jokeapi.Jokes()
    raw_joke = await j.get_joke(safe_mode=True)
    embed = hikari.Embed(title="J.O.K.E", description='', color=ctx.author.accent_colour)
    if raw_joke['type'] == "single":
        embed.description = raw_joke['joke']
    else:
        embed.description = f"{raw_joke['setup']}\n{raw_joke['delivery']}"
    await ctx.respond(embed=embed)

@fun.command
@lightbulb.command(name="meme", description="Get a meme", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_meme(ctx: lightbulb.SlashContext):
    resp = await fun.bot.http.get("https://meme-api.herokuapp.com/gimme")
    content = await resp.json()
    embed = hikari.Embed(title= content["title"], description=f"By: {content['author']}", color=ctx.author.accent_color).set_footer(text=f"Reddit Page: {content['postLink']}").set_image(content["url"])
    await ctx.respond(embed=embed)

def load(bot: Yuuki) -> None:
    bot.add_plugin(fun)