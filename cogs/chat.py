# coding: utf-8

# standard
import configparser
import time
import urllib3
import re
import requests

# bs4
from bs4 import BeautifulSoup

# discord
import discord
from discord.ext import commands

# deepl
import deepl

# google
# official google search api
from googleapiclient.discovery import build
# unofficial google search api
import googlesearch
# unofficial google translate api
import googletrans

# unofficial chatgpt api
from revChatGPT.V1 import Chatbot

class Chat(commands.Cog, name='Chat'):

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

        # read config
        config = configparser.ConfigParser()
        config.read('config.ini')

        # icons
        self.ICON_DEEPL = config['ICON']['deepl']
        self.ICON_GOOGLE = config['ICON']['google']
        self.ICON_GOOGLEMAP = config['ICON']['googlemap']
        self.ICON_GOOGLENEWS = config['ICON']['googlenews']
        self.ICON_GOOGLETRANS = config['ICON']['googletrans']
        self.ICON_OPENAI = config['ICON']['openai']
        self.ICON_YAHOO = config['ICON']['yahoo']

        # deepl
        self.deepl = deepl.Translator(config['DEEPL']['key'])
        # google
        self.customsearch = build("customsearch", "v1", developerKey=config['GOOGLE']['customsearch_key'])
        self.customsearch_id = config['GOOGLE']['customsearch_id']
        self.SEARCH_MAX = 10
        self.googletrans = googletrans.Translator()
        # openai
        self.chatbot = Chatbot(config={'email': config['OPENAI']['email'], 'password': config['OPENAI']['password']})

    async def cog_check(self, ctx: commands.Context) -> bool:
        if ctx.author.bot:
            return False
        else:
            return True

    @commands.hybrid_command(name='help_', aliases=['h_'], description='help')
    async def help(self, ctx: commands.Context) -> None:
        embed = discord.Embed(color=0x000000, title='Help', description='This is a help message.')
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.add_field(name='ping', value='pong', inline=False)
        embed.add_field(name='askai', value='ask ai', inline=False)
        embed.add_field(name='map', value='map', inline=False)
        embed.add_field(name='news', value='news', inline=False)
        embed.add_field(name='search', value='search', inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='ping', aliases=['p'], description='pong')
    async def ping(self, ctx: commands.Context) -> None:
        await ctx.send('pong')

    @commands.hybrid_command(name='askai', aliases=['ai'], description='ask ai')
    async def askai(self, ctx: commands.Context, message: str, engine: str='c3.5') -> None:
        await ctx.defer()
        embed = discord.Embed(color=0x000000, title=message, description="...")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed_id = await ctx.send(embed=embed)

        try:
            if engine == 'c3.5':
                embed.color = 0x7ea79c
                embed.set_footer(text='GPT-3.5 architecture based ChatGPT', icon_url=self.ICON_OPENAI)

                try:
                    ## unofficial chatgpt api
                    elapsed_time = time.time()
                    for data in self.chatbot.ask(message):
                        embed.title = '[💬] '+message
                        embed.description = data["message"]
                        # update every 1 sec.
                        if time.time() - elapsed_time > 1:
                            elapsed_time = time.time()
                            await embed_id.edit(embed=embed)
                    ## end
                except Exception as e:
                    raise Exception(e)
            else:
                raise Exception('Invalid engine. Please use "c3.5".')
        except Exception as e:
            embed.title = '[❌] '+message
            embed.description = f'Internal error: {e}'
        else:
            embed.title = '[✅] '+message
        finally:
            await embed_id.edit(embed=embed)

    @commands.hybrid_command(name='map', aliases=['m'], description='map')
    async def map(self, ctx: commands.Context, query: str, engine: str='g') -> None:
        pass

    @commands.hybrid_command(name='news', aliases=['n'], description='news')
    async def news(self, ctx: commands.Context, lang='jp', query: str='', engine: str='y') -> None:
        pass

    @commands.hybrid_command(name='search', aliases=['s'], description='search')
    async def search(self, ctx: commands.Context, query: str, count: int=1, engine: str='g') -> None:
        count = int(count)
        if  count > self.SEARCH_MAX:
            count = self.SEARCH_MAX

        await ctx.defer()
        embed = discord.Embed(color=0x000000, title=query, description='')
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed_id = await ctx.send(embed=embed)

        try:
            if engine == 'g':
                embed.set_footer(text='Google Search', icon_url=self.ICON_GOOGLE)

                try:
                    ## official google search api
                    #for i, result in enumerate(self.customsearch.cse().list(q=query, cx=self.customsearch_id, num=count).execute()['items']):
                    #    embed.title = f'[🔍 ({i}/{count})] '+query
                    #    embed.description += f'・[{result["title"]}]({result["link"]})\n'
                    ## end

                    ## unofficial google search api
                    for i, url in enumerate(googlesearch.search(query, num_results=count, lang='ja')):
                        embed.title = f'[🔍 ({i+1}/{count})] '+query
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
                except Exception as e:
                    raise Exception(e)
            else:
                raise Exception('Invalid engine. Please use "g."')
        except Exception as e:
            embed.title = '[❌] '+query
            embed.description = f'Internal error: {e}'
        else:
            embed.title = f'[✅ ({count})] '+query
        finally:
            await embed_id.edit(embed=embed)

    @commands.hybrid_command(name='topic', aliases=['t'], description='topic')
    async def topic(self, ctx: commands.Context, lang='jp', engine: str='y') -> None:
        topics = []
        await ctx.defer()
        embed = discord.Embed(color=0x000000, title='Getting news...', description='')
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed_id = await ctx.send(embed=embed)

        try:
            if engine == 'g' and lang == 'jp':
                embed.set_footer(text='Google News', icon_url=self.ICON_GOOGLENEWS)
            elif engine == 'y' and lang == 'jp':
                embed.set_footer(text='Yahoo! News', icon_url=self.ICON_YAHOO)
                ## unofficial yahoo news api
                res = requests.get('https://www.yahoo.co.jp/')
                soup = BeautifulSoup(res.text, 'html.parser')
                for i, news in enumerate(soup.find_all(href=re.compile('news.yahoo.co.jp/pickup'))):
                    topics.append(f'・[{news.text}]({news["href"]})')
                    await embed_id.edit(embed=embed)
                ## end
            else:
                raise Exception('Invalid engine or language. Please use "g" or "y" for engine and "jp" for language.')
        except Exception as e:
            embed.title = '[❌] '
            embed.description = f'Internal error: {e}'
        else:
            embed.title = f'[✅ ({len(topics)})] '
            embed.description = '\n'.join(topics)
        finally:
            await embed_id.edit(embed=embed)

    @commands.hybrid_command(name='translate', aliases=['tl'], description='translate')
    async def translate(self, ctx: commands.Context, message: str, src: str='auto', dest: str='en', engine: str='g') -> None:
        await ctx.defer()
        embed = discord.Embed(color=0x000000, title=message, description="...")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed_id = await ctx.send(embed=embed)

        try:
            if engine == 'd':
                embed.set_footer(text='DeepL', icon_url=self.ICON_DEEPL)

                ## official deepl api
                result = self.deepl.translate_text(text=message, source_lang=src, target_lang=dest)
                ## end

            if engine == 'g':
                embed.set_footer(text='Google Translate', icon_url=self.ICON_GOOGLETRANS)

                ## unofficial google translate api
                result = self.googletrans.translate(text=message, dest=dest, src=src)
                ## end
            else:
                raise Exception('Invalid engine. Please use "g."')
        except Exception as e:
            embed.title = '[❌] '+message
            embed.description = f'Internal error: {e}'
        else:
            embed.title = f'[✅ ({result.src} -> {result.dest})] '+message
            embed.description = result.text
        finally:
            await embed_id.edit(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Chat(bot))

