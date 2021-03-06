# MIT License
#
# Copyright (c) 2021 Compass
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import discord
import objectfile
import sr_api
import yaml
import pycountry
from MojangAPI import Client
import cse
import random
import aiohttp
import asyncpraw
from discord.ext import commands

config = yaml.safe_load(open("config.yml"))
client = sr_api.Client(config['srakey'])
reddit = asyncpraw.Reddit(client_id=config['redditauth'][1], client_secret=config['redditauth'][0],
                          password=config['password'], user_agent=config['redditauth'][2],
                          username="Sovietica")
engine = cse.Search(config['googleapikey'])
info_or_flag = ['country info', 'country flag', 'country stats']
country_commands = ['country info', 'country flag', 'country subdivision', 'country stats']

class APIs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 5)
    @commands.command()
    async def google(self, ctx, *, arg):
        try:
            results = await engine.search(f"{arg}")
            if results[0].snippet is not None:
                snippet = str(results[0].snippet)
            if results[0].snippet is None:
                snippet = "No snippet available."
            embed = objectfile.twoembed(results[0].title,
                                        snippet)
            embed.add_field(name="URL", value=results[0].link, inline=True)
            embed.set_image(url=f"{results[0].image}")
            await ctx.send(embed=embed)
        except KeyError:
            await ctx.send(embed=objectfile.newfailembed("No results!",
                                                         "Try searching something else."))

    @commands.command()
    async def priorityqueue(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://api.2b2t.dev/prioq") as q:
                queueapi = await q.json()
                embed = discord.Embed(colour=0x202225, title='2b2t Priority Queue Stats')
                embed.add_field(name='Users In Queue', value=str(queueapi[1]), inline=True)
                embed.add_field(name='ETA to join 2b2t', value=str(queueapi[2]), inline=True)
                embed.set_footer(text='Courtesy of https://2b2t.dev | https://api.2b2t.dev/prioq')
                await ctx.send(embed=embed)

    @commands.command(name="2b2tlastseen")
    async def lastseen(self, ctx, *, arg):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://api.2b2t.dev/seen?username={arg}") as l:
                lastseenapi = await l.json()
                embed = discord.Embed(colour=0x202225, title=f"{arg} was last seen at...")
                embed.add_field(name=f'All times in EDT',
                                value=f"{lastseenapi['seen']}", inline=True)
                embed.set_footer(text=f'Courtesy of https://2b2t.dev | https://api.2b2t.dev/seen?username={arg}')
                await ctx.send(embed=embed)

    @commands.command()
    async def normalqueue(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://2b2t.io/api/queue?last=true") as q:
                queueapiraw = str(await q.read()).replace("[[", "").replace("]]'", "").split(",")
                embed = discord.Embed(colour=discord.Colour.from_rgb(122, 141, 207), title="2b2t Normal Queue Stats")
                embed.add_field(name='Users In Queue', value=queueapiraw[1], inline=True)
                embed.set_footer(text='Courtesy of https://2b2t.io | https://2b2t.io/api/queue?last=true')
                await ctx.send(embed=embed)

    @commands.command()
    async def totalqueue(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://api.2b2t.dev/prioq") as prioqapi:
                prioqueueraw = await prioqapi.json()
            async with cs.get(f"https://2b2t.io/api/queue?last=true") as normalqapi:
                normalqapiraw = str(await normalqapi.read()).replace("[[", "").replace("]]'", "").split(",")
            embed = objectfile.twoembed("Total players in the 2b2t queue!",
                                        int(prioqueueraw[1]) + int(normalqapiraw[1]))
            embed.set_footer(
                text='Courtesy of https://api.2b2t.dev/prioq | https://2b2t.io/api/queue?last=true')
            await ctx.send(embed=embed)

    @commands.command()
    async def playercount(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://api.hypixel.net/playerCount?key={config['hypixelapikey']}") as playercountraw:
                playercount = await playercountraw.json()
                embed = objectfile.twoembed("Hypixel Player Count",
                                            "{:,}".format(int(playercount['playerCount'])))
                embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/en/9/93/HypixelLogo.png")
                await ctx.send(embed=embed)

    @commands.command()
    async def watchdog(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://api.hypixel.net/watchdogstats?key={config['hypixelapikey']}") as watchdogstats:
                watchdog = await watchdogstats.json()
                embed = objectfile.twoembed("Hypixel Watchdog Stats",
                                            "Don't break the rules!")
                embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/en/9/93/HypixelLogo.png")
                embed.add_field(name="Bans in the last minute",
                                value="{:,}".format(int(watchdog['watchdog_lastMinute'])))
                embed.add_field(name="Staff Rolling Daily", value="{:,}".format(int(watchdog['staff_rollingDaily'])))
                embed.add_field(name="Watchdog Rolling Daily",
                                value="{:,}".format(int(watchdog['watchdog_rollingDaily'])))
                embed.add_field(name="Total Watchdog Bans", value="{:,}".format(int(watchdog['watchdog_total'])))
                embed.add_field(name="Total Staff Bans", value="{:,}".format(int(watchdog['staff_total'])))
                await ctx.send(embed=embed)

    @commands.command()
    async def skin(self, ctx, username):
        user = await Client.User.createUser(username)
        profile = await user.getProfile()
        embed = objectfile.twoembed(f"{username}'s Minecraft skin!",
                                    "This API hurts.")
        embed.set_image(url=profile.skin)
        await ctx.send(embed=embed)

    @commands.command()
    async def gamecount(self, ctx, *, game_name):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://api.hypixel.net/gameCounts?key={config['hypixelapikey']}") as gamecountstats:
                stats = await gamecountstats.json()
                embed = objectfile.twoembed(f"Game stats for {game_name}",
                                            "Stats go brrr!")
                embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/en/9/93/HypixelLogo.png")
                embed.add_field(name="Player Count",
                                value="{:,}".format(int(stats['games'][game_name.upper()]['players'])))
                await ctx.send(embed=embed)

    @commands.command()
    async def cat(self, ctx):
        # Get image
        image = await client.get_image("cat")
        await image.save("image.png")
        # File
        file = discord.File("image.png", filename="image.png")
        # Embed
        embed = discord.Embed(color=0x202225, title="Your cat!")
        embed.set_image(url="attachment://image.png")
        await ctx.send(embed=embed, file=file)

    @commands.command()
    async def dog(self, ctx):
        # Get image
        image = await client.get_image("dog")
        await image.save("image.png")
        # File
        file = discord.File("image.png", filename="image.png")
        # Embed
        embed = discord.Embed(color=0x202225, title="Your dog!")
        embed.set_image(url="attachment://image.png")
        await ctx.send(embed=embed, file=file)

    @commands.command()
    async def pokemon(self, ctx, *, arg):
        # Grab pokemon
        pokemon = await client.get_pokemon(name=arg)
        # Embed it
        gender = str(pokemon.gender).replace("['", "").replace("']", "").replace("'", "")
        egg_groups = str(pokemon.egg_groups).replace("['", "").replace("']", "").replace("'", "")
        evolution_line = str(pokemon.evolutionLine).replace("['", "").replace("']", "").replace("'", "")
        abilities = str(pokemon.abilities)
        embed = discord.Embed(color=0x202225, title=pokemon.name)
        embed.add_field(name="ID", value=pokemon.id, inline=False)
        embed.add_field(name="Type", value=str(pokemon.type).replace("['", "").replace("']", "").replace("'", ""),
                        inline=False)
        embed.add_field(name="Description", value=pokemon.description, inline=False)
        embed.add_field(name="Biology", value=f"Height: {pokemon.height}\nWeight: {pokemon.weight}\n"
                                              f"Gender: {gender}\nEgg Groups: {egg_groups}\n",
                        inline=False)
        embed.add_field(name="Evolution", value=f"Evolution Stage: {pokemon.evolutionStage}\n"
                                                f"Evolution Line: {evolution_line}\n"
                                                f"Generation: {pokemon.generation}", inline=False)
        embed.add_field(name="Battle Stats", value=f"Abilities: {abilities}\n"
                                                   f"Base Experience: {pokemon.base_experience}\n"
                                                   f"HP: {pokemon.hp}\n"
                                                   f"Attack: {pokemon.attack}\n"
                                                   f"Defense: {pokemon.defense}\n"
                                                   f"Special Attack: {pokemon.sp_atk}\n"
                                                   f"Special Defense: {pokemon.sp_def}\n"
                                                   f"Speed: {pokemon.speed}\n"
                                                   f"Total Stats: {pokemon.total}")
        await ctx.send(embed=embed)

    @commands.command()
    async def namehistory(self, ctx, *, arg):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f'https://playerdb.co/api/player/minecraft/{arg}') as idapiraw:
                idapi = str(idapiraw).replace("{", "").replace("}", "").replace('"', "").replace("id:", "").replace(
                    "avatar:",
                    "").split(
                    ",")
                userid = idapi[10]
                mcuser = await client.mc_user(arg)
                embed = discord.Embed(color=0x202225, title=f"{arg}'s name history!")
                embed.add_field(name="UUID", value=userid, inline=False)
                embed.add_field(name="Minecraft Name History", value=mcuser.formatted_history, inline=False)
                embed.set_footer(
                    text=f"APIs courtesy of https://crafatar.com and https://playerdb.co/api/player/minecraft/{arg}")
                await ctx.send(embed=embed)

    @commands.command()
    async def kanye(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://api.kanye.rest') as r:
                res = await r.json()
                embed = objectfile.twoembed("Your Kanye quote!",
                                            res['quote'])
                await ctx.send(embed=embed)

    @commands.command()
    async def covid(self, ctx, *, arg):
        async with aiohttp.ClientSession() as cs:
            if arg in objectfile.usstates:
                async with cs.get(
                        f'https://corona.lmao.ninja/v3/covid-19/states/{arg}?yesterday=true&strict=true&query') as r:
                    res = await r.json()
                    embed = objectfile.twoembed(f"Yesterday's COVID cases in {arg.capitalize()}",
                                                random.choice(['Wash your hands!', 'Stay 6 feet away!',
                                                               'Apply common sense!']))
                    embed.add_field(name="Total Cases", value="{:,}".format(int(res['cases'])), inline=False)
                    embed.add_field(name="Total Deaths", value="{:,}".format(int(res['deaths'])), inline=False)
                    embed.add_field(name="Total Recoveries", value="{:,}".format(int(res['recovered'])), inline=False)
                    embed.add_field(name="Daily Cases", value="{:,}".format(int(res['todayCases'])), inline=True)
                    embed.add_field(name="Daily Deaths", value="{:,}".format(int(res['todayDeaths'])), inline=True)
                    embed.add_field(name="Active Cases", value="{:,}".format(int(res['active'])), inline=False)
                    await ctx.send(embed=embed)
                    return
            else:
                async with cs.get(
                        f'https://corona.lmao.ninja/v2/countries/{arg}?yesterday=true&strict=true&query') as r:
                    res = await r.json()
                    if res['cases'] is None:
                        await ctx.send(embed=objectfile.twoembed(f"{arg.capitalize()} isn't a country!",
                                                                 "Check your spelling, or search for a real country."))
                        return
                    else:
                        embed = objectfile.twoembed(f"Yesterday's COVID cases in {arg.capitalize()}",
                                                    random.choice(['Wash your hands!', 'Stay 6 feet away!',
                                                                   'Apply common sense!']))
                        embed.add_field(name="Total Cases", value="{:,}".format(int(res['cases'])), inline=False)
                        embed.add_field(name="Total Deaths", value="{:,}".format(int(res['deaths'])), inline=False)
                        embed.add_field(name="Total Recoveries", value="{:,}".format(int(res['recovered'])),
                                        inline=False)
                        embed.add_field(name="Daily Cases", value="{:,}".format(int(res['todayCases'])), inline=True)
                        embed.add_field(name="Daily Deaths", value="{:,}".format(int(res['todayDeaths'])), inline=True)
                        embed.add_field(name="Daily Recoveries", value="{:,}".format(int(res['todayRecovered'])),
                                        inline=True)
                        embed.add_field(name="Active Cases", value="{:,}".format(int(res['active'])), inline=False)
                        embed.set_thumbnail(url=res['countryInfo']['flag'])
                        await ctx.send(embed=embed)

    @commands.command()
    async def pypi(self, ctx, *, arg):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                    f'https://pypi.org/pypi/{arg}/json') as r:
                res = await r.json()
                embed = objectfile.twoembed(f"PyPI stats for {arg}",
                                            f"{res['info']['project_urls']['homepage']} {res['info']['project_urls']['docs_url']}")
                embed.add_field(name="Author", value=res['info']['author'], inline=False)
                embed.add_field(name="Description", value=res['info']['description'], inline=False)
                embed.add_field(name="Downloads over 1 week", value=res['info']['last_week'], inline=False)
                embed.add_field(name="Keywords", value=res['info']['keywords'], inline=True)
                embed.add_field(name="Version", value=res['info']['version'], inline=True)
                embed.add_field(name="Python Version", value=res['info']['python_version'], inline=True)
                embed.add_field(name="Classifiers", value=res['info']['classifiers'], inline=True)
                await ctx.send(embed=embed)

    @commands.command()
    async def weather(self, ctx, *, arg=None):
        if arg is None:
            await ctx.send(embed=objectfile.twoembed("You need to search for something!",
                                                     "Example: compass!weather Atlanta, GA"))
        else:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(
                        f"http://api.openweathermap.org/data/2.5/weather?appid={config['weatherapikey']}&q={arg}") as r:
                    x = await r.json()
                    if x["cod"] != "404":
                        embed = objectfile.twoembed(f"{arg}'s weather!",
                                                    f"{str(x['weather'][0]['description'])}\n"
                                                    f"Humidity: {x['main']['humidity']}\n"
                                                    f"Temperature (Celsius): {str(round(x['main']['temp'] - 273.15))}\n"
                                                    f"Temperature (Fahrenheit): {str(round((round(x['main']['temp'] - 273.15) * 9 / 5) + 32))}\n "
                                                    f"Pressure: {x['main']['pressure']}\n")
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(embed=objectfile.twoembed("This place doesn't exist!",
                                                                 "Try searching for something else.\n"
                                                                 "Example: compass!weather Atlanta, GA"))

    @commands.command()
    async def urban(self, ctx, *, arg):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://urbanscraper.herokuapp.com/define/{arg}") as urbanraw:
                urbanraw = await urbanraw.json()
                embed = discord.Embed(title=f'{arg} | #{urbanraw["id"]}', description=str(urbanraw["definition"]).replace(r"\r", "\n"), color=0x202225)
                embed.add_field(name="Examples", value=str(urbanraw["example"]).replace(r"\r", "\n"))
                embed.set_footer(text=f'{urbanraw["url"]} | Courtesy of https://urbanscraper.herokuapp.com/')
                await ctx.send(embed=embed)

    @commands.command()
    async def taylor(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://api.taylor.rest") as taylorquoteraw:
                taylorquoteget = await taylorquoteraw.json()
                embed = objectfile.twoembed("Your Taylor Swift quote!",
                                            taylorquoteget['quote'])
            async with cs.get(f"https://api.taylor.rest/image") as imageraw:
                imagegrab = await imageraw.json()
                embed.set_thumbnail(url=imagegrab['url'])
                await ctx.send(embed=embed)

    @commands.command()
    async def inspirobot(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://inspirobot.me/api?generate=true") as inspirobotraw:
                read = str(await inspirobotraw.read()).replace("b'", "").replace("'", "")
                embed = objectfile.twoembed("An inspirational quote!",
                                            f"[URL]({read})")
                embed.set_image(url=read)
                await ctx.send(embed=embed)

    @commands.command()
    async def reddit(self, ctx):
        subreddit = await reddit.subreddit("dankmemes")
        async for submission in subreddit.random_rising(limit=1):
            embed = objectfile.twoembed(f"{submission.title} | #{submission.id}",
                                        f"{submission.score} upvotes")
            embed.set_image(url=submission.url)
            await ctx.send(embed=embed)

    @commands.command()
    async def yesorno(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://yesno.wtf/api") as rawversion:
                yes_or_no_api = await rawversion.json()
                if yes_or_no_api['answer'] == "yes":
                    emoji = self.bot.get_emoji(797916243281707008)
                if yes_or_no_api['answer'] == "no":
                    emoji = self.bot.get_emoji(797916257558331432)
                if yes_or_no_api['answer'] == "maybe":
                    emoji = self.bot.get_emoji(798298058495361025)
                embed = objectfile.imgembed(f"{emoji} {str(yes_or_no_api['answer']).title()}.",
                                            yes_or_no_api['image'])
                await ctx.send(embed=embed)

    @commands.command()
    async def iss(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get("http://api.open-notify.org/iss-now") as raw:
                iss_info = await raw.json()
                embed = objectfile.twoembed("Location of the International Space Station!",
                                            "Up, up and away.")
                embed.add_field(name="Longitude", value=iss_info['iss_position']['longitude'], inline=True)
                embed.add_field(name="Latitude", value=iss_info['iss_position']['latitude'], inline=True)
                await ctx.send(embed=embed)

    @commands.command()
    async def space(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://api.nasa.gov/planetary/apod?api_key={config['nasakey']}") as nasa_raw:
                nasa_json = await nasa_raw.json()
                embed = objectfile.twoembed(nasa_json['title'],
                                            nasa_json['explanation'])
                if 'copyright' in nasa_json:
                    embed.add_field(name="Copyright", value=nasa_json['copyright'], inline=True)
                embed.set_image(url=nasa_json['hdurl'])
                await ctx.send(embed=embed)

    @commands.command()
    async def imdb(self, ctx, *, id: str):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://www.omdbapi.com/?i={id}&apikey=eb3aed44") as raw_omdb:
                json_omdb = await raw_omdb.json()
                embed = objectfile.twoembed(json_omdb['Title'],
                                            json_omdb['Plot'])
                embed.add_field(name="Genre", value=json_omdb['Genre'], inline=False)
                embed.add_field(name="Director", value=json_omdb['Director'], inline=True)
                embed.add_field(name="Writer", value=json_omdb['Writer'], inline=True)
                embed.add_field(name="Actors", value=json_omdb['Actors'], inline=True)
                embed.add_field(name="Release Date", value=json_omdb['Released'], inline=False)
                embed.add_field(name="Runtime", value=json_omdb['Runtime'], inline=False)
                embed.add_field(name="Rated", value=json_omdb['Rated'], inline=False)
                embed.add_field(name="Ratings",
                                value=f"IMD: {json_omdb['Ratings']['Source']['Internet Movie Database']['Value']}\n"
                                      f"Rotten Tomatoes: {json_omdb['Ratings']['Source']['Rotten Tomatoes']['Value']}\n"
                                      f"Metacritic: {json_omdb['Ratings']['Source']['Metacritic']['Value']}\n"
                                      f"IMDB: {json_omdb['imdbRating']}", inline=False)
                embed.add_field(name="Box Office", value=json_omdb['BoxOffice'], inline=False)
                await ctx.send(embed=embed)

    @commands.group()
    async def trump(self, ctx):
        if ctx.invoked_subcommand is None:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://api.tronalddump.io/random/quote') as r:
                    res = await r.json()
                    embed = objectfile.twoembed("Your Trump quote!",
                                                res['value'])
                    embed.set_thumbnail(
                        url="https://cdn.discordapp.com/attachments/777248921205866546/797288910282948608/kUuht00m.png")
                    await ctx.send(embed=embed)
                    return

    async def no_country_name(self, command):
        example = f""
        type = f""
        if command in info_or_flag:
            type += f"country"
            example += f"Example; compass!{command} USA"
        else:
            type += f"subdivision"
            example += f"Example; compass!{command} US-GA"
        embed = objectfile.newfailembed(f"You need a {type}!",
                                        example)
        return embed

    @commands.group()
    async def country(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=objectfile.twoembed("Available subcommands for compass!country;",
                                                     "compass!country info (or stats), compass!country flag,\n"
                                                     "compass!country subdivisions."))

    @country.command(aliases=['stats'])
    async def info(self, ctx, *, country_name=None):
        if country_name is None:
            await ctx.send(embed=await self.no_country_name(ctx.command.qualified_name))
        else:
            country_search = pycountry.countries.get(name=str(
                country_name.replace("USA", "United States").replace("usa", "United States").replace("Usa",
                                                                                                     "United States").replace(
                    "US", "United States")))
            embed = objectfile.twoembed(f"{country_search.name}'s stats!",
                                        f"Alpha: {country_search.alpha_2}/{country_search.alpha_3}\n"
                                        f"Numeric: {country_search.numeric}\n"
                                        f"Wikipedia Page: [URL](https://en.wikipedia.org/wiki/{str(country_search.name).replace(' ', '_')})")
            embed.set_thumbnail(url=f"https://flagpedia.net/data/flags/w702/{country_search.alpha_2.lower()}.png")
            await ctx.send(embed=embed)

    @country.command(aliases=['subdivision', 'province', 'state'])
    async def subdivisions(self, ctx, *, subdivision_name: str = None):
        if subdivision_name is None:
            await ctx.send(embed=await self.no_country_name(ctx.command.qualified_name))
        else:
            subdivision_search = pycountry.subdivisions.get(code=str(subdivision_name))
            embed = objectfile.twoembed(f"{subdivision_search.code}'s stats!",
                                        f"Name: {subdivision_search.name}\n"
                                        f"Type: {subdivision_search.type}\n")
            await ctx.send(embed=embed)

    @country.command()
    async def flag(self, ctx, *, country_name: str = None):
        if country_name is None:
            await ctx.send(embed=await self.no_country_name(ctx.command.qualified_name))
        else:
            country_search = pycountry.countries.get(name=str(
                country_name.replace("USA", "United States").replace("usa", "United States").replace("Usa",
                                                                                                     "United States").replace(
                    "US", "United States")))
            embed = objectfile.imgembed(f"The flag of {country_search.name}!",
                                        f"https://flagpedia.net/data/flags/w702/{country_search.alpha_2.lower()}.png")
            await ctx.send(embed=embed)

    @commands.command(name="encodeinbinary")
    async def _encodeinbinary(self, ctx, *, arg):
        text = arg
        binary = await client.encode_binary(text)
        embed = objectfile.twoembed(f"{text} encoded!", binary)
        await ctx.send(embed=embed)

    @commands.command(name="decodeinbinary")
    async def _decodeinbinary(self, ctx, *, arg):
        binary = arg
        decodedtext = await client.decode_binary(binary)
        embed = objectfile.twoembed(f"{binary} decoded!", decodedtext)
        await ctx.send(embed=embed)

    @commands.command(name="encodeinbase64")
    async def _encodeinbase64(self, ctx, *, arg):
        text = arg
        encoded = await client.encode_base64(text)
        embed = objectfile.twoembed(f"{text} encoded!", encoded)
        await ctx.send(embed=embed)

    @commands.command(name="decodeinbase64")
    async def _decodeinbase64(self, ctx, *, arg):
        text = arg
        decodedtext = await client.decode_base64(text)
        embed = objectfile.twoembed(f"{text} decoded!", decodedtext)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(APIs(bot))
