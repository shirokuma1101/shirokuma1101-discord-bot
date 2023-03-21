# coding: utf-8

# standard
import configparser
import time
import urllib3

# discord
import discord
from discord.ext import commands

# bs4
from bs4 import BeautifulSoup

# google
# official google search api
from googleapiclient.discovery import build
# unofficial google search api
from googlesearch import search
# unofficial google translate api
from googletrans import Translator

# unofficial chatgpt api
from revChatGPT.V1 import Chatbot

class Chat(commands.Cog, name='Chat'):

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

        # read config
        config = configparser.ConfigParser()
        config.read('config.ini')
        # openai
        self.chatbot = Chatbot(config={'email': config['OPENAI']['email'], 'password': config['OPENAI']['password']})
        # google
        self.customsearch = build("customsearch", "v1", developerKey=config['GOOGLE']['customsearch_key'])
        self.customsearch_id = config['GOOGLE']['customsearch_id']
        self.SEARCH_MAX = 10
        self.translator = Translator()

    async def cog_check(self, ctx: commands.Context):
        if ctx.author.bot:
            return False
        else:
            return True

    @commands.hybrid_command(name='ping', aliases=['p'], description='pong')
    async def ping(self, ctx: commands.Context) -> None:
        await ctx.send('pong')

    @commands.hybrid_command(name='askai', aliases=['ai'], description='ask ai')
    async def askai(self, ctx: commands.Context, message: str, engine: str='c3.5') -> None:
        await ctx.defer()
        embed = discord.Embed(color=0x7ea79c, title=message, description="...")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        if engine == 'c3.5':
            embed.set_footer(text='GPT-3.5 architecture based ChatGPT', icon_url='https://cdn.discordapp.com/avatars/1046280307462123561/ed2bda6bcbe4264c19a51663adcae15b.webp')
        embed_id = await ctx.send(embed=embed)

        try:
            elapsed_time = time.time()
            for data in self.chatbot.ask(message):
                embed.title = '[💬] '+message
                embed.description = data["message"]
                # update every 1 sec.
                if time.time() - elapsed_time > 1:
                    elapsed_time = time.time()
                    await embed_id.edit(embed=embed)
        except Exception as e:
            embed.title = '[❌] '+message
            embed.description = 'The answer could not be found or there may have been an internal error.'
        else:
            embed.title = '[✅] '+message
        finally:
            await embed_id.edit(embed=embed)

    @commands.hybrid_command(name='search', aliases=['s'], description='search')
    async def search(self, ctx: commands.Context, query: str, count: int=1, engine: str='g') -> None:
        await ctx.defer()
        embed = discord.Embed(color=0x000000, title=query, description='')
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_footer(text='Google')
        embed_id = await ctx.send(embed=embed)

        count = int(count)
        if  count > self.SEARCH_MAX:
            count = self.SEARCH_MAX

        try:
            if engine == 'g':
                ## unofficial google search api
                for i, url in enumerate(search(query, num_results=count, lang='ja')):
                    embed.title = f'[🔍({i+1}/{count})] '+query
                    http = urllib3.PoolManager()
                    soup = BeautifulSoup(http.request('GET', url).data, 'html.parser')
                    try:
                        title = soup.find('title').text
                    except:
                        pass
                    else:
                        embed.description += f'・[{title}]({url})\n'
                        await embed_id.edit(embed=embed)

                    # search function returns more than 1 result when num_results is 1
                    if i == count-1:
                        break
                ## end

                ## official google search api
                #for i, result in enumerate(self.customsearch.cse().list(q=query, cx=self.customsearch_id, num=count).execute()['items']):
                #    embed.title = f'[🔍({i}/{count})] '+query
                #    embed.description += f'・[{result["title"]}]({result["link"]})\n'
                ## end
        except Exception as e:
            print(e)
            embed.title = '[❌] '+query
            embed.description = 'The search could not be found or there may have been an internal error.'
        else:
            embed.title = f'[✅ ({count})] '+query
        finally:
            await embed_id.edit(embed=embed)

    @commands.hybrid_command(name='translate', aliases=['t'], description='translate')
    async def translate(self, ctx: commands.Context, message: str, src: str='auto', dest: str='en', engine: str='g') -> None:
        await ctx.defer()
        embed = discord.Embed(color=0x000000, title=message, description="...")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_footer(text='Google')
        embed_id = await ctx.send(embed=embed)

        try:
            if engine == 'g':
                ## unofficial google translate api
                result = self.translator.translate(message, dest=dest, src=src)
                embed.title = '[🌐] '+message
                embed.description = result.text
                ## end
        except Exception as e:
            embed.title = '[❌] '+message
            embed.description = 'The translation could not be found or there may have been an internal error.'
        else:
            embed.title = f'[✅ ({result.src} -> {result.dest})] '+message
        finally:
            await embed_id.edit(embed=embed)


async def setup(bot):
    await bot.add_cog(Chat(bot))

