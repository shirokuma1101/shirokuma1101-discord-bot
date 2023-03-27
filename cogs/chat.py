# coding: utf-8

# standard
import configparser
import time
import urllib3
import re
import requests

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

        # icons
        self.ICON_OPENAI = 'https://cdn.discordapp.com/avatars/1046280307462123561/ed2bda6bcbe4264c19a51663adcae15b.webp'
        self.ICON_GOOGLE = 'https://lh3.googleusercontent.com/COxitqgJr1sJnIDe8-jiKhxDx1FrYbtRHKJ9z_hELisAlapwE9LUPh6fcXIfb5vwpbMl4xl9H9TRFPc5NOO8Sb3VSgIBrfRYvW6cUA'
        self.ICON_GOOGLEMAP = 'https://lh3.googleusercontent.com/V0Lu6YzAVaCVcjSJ_4Qb0mR_idw-GApETGbkodvDKTH-rpDvHuD6J84jshR_FvXdl5mJxqbIHVdebYCCbQMJNxIxRaIHYFSq6z7laA'
        self.ICON_GOOGLENEWS = 'https://lh3.googleusercontent.com/9agKA1CG--ihx80qoPwq8xVFZ0i0_nEyLpXlcf8juPbFXe13GhUBR7Y5xOO3LVfnmM06OtrWw086uFlQ9s5jNPlvXJNBQViCvB4L4Q'
        self.ICON_GOOGLETRANS = 'https://storage.googleapis.com/gweb-uniblog-publish-prod/original_images/logo_translate_color_2x_web_512dp.png'
        self.ICON_YAHOO = 'https://s.yimg.jp/images/top/sp2/cmn/logo-170307.png'

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

    @commands.hybrid_command(name='help', aliases=['h'], description='help')
    async def help(self, ctx: commands.Context) -> None:
        pass

    @commands.hybrid_command(name='ping', aliases=['p'], description='pong')
    async def ping(self, ctx: commands.Context) -> None:
        await ctx.send('pong')

    @commands.hybrid_command(name='askai', aliases=['ai'], description='ask ai')
    async def askai(self, ctx: commands.Context, message: str, engine: str='c3.5') -> None:
        await ctx.defer()
        embed = discord.Embed(color=0x7ea79c, title=message, description="...")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        if engine == 'c3.5':
            embed.set_footer(text='GPT-3.5 architecture based ChatGPT', icon_url=self.ICON_OPENAI)
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
        embed.set_footer(text='Google Search', icon_url=self.ICON_GOOGLE)
        embed_id = await ctx.send(embed=embed)

        try:
            if engine == 'g':
                ## unofficial google search api
                for i, url in enumerate(search(query, num_results=count, lang='ja')):
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

                ## official google search api
                #for i, result in enumerate(self.customsearch.cse().list(q=query, cx=self.customsearch_id, num=count).execute()['items']):
                #    embed.title = f'[🔍 ({i}/{count})] '+query
                #    embed.description += f'・[{result["title"]}]({result["link"]})\n'
                ## end
            else:
                embed.description = 'The search engine is not supported.'
        except Exception as e:
            print(e)
            embed.title = '[❌] '+query
            embed.description = 'The search could not be found or there may have been an internal error.'
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
                embed.description = 'The news engine is not supported.'
        except Exception as e:
            embed.title = '[❌] '
            embed.description = 'The news could not be found or there may have been an internal error.'
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
        embed.set_footer(text='Google Translate', icon_url=self.ICON_GOOGLETRANS)
        embed_id = await ctx.send(embed=embed)

        try:
            if engine == 'g':
                ## unofficial google translate api
                result = self.translator.translate(message, dest=dest, src=src)
                embed.title = '[🌐] '+message
                embed.description = result.text
                ## end
            else:
                embed.description = 'The translation engine is not supported.'
        except Exception as e:
            embed.title = '[❌] '+message
            embed.description = 'The translation could not be found or there may have been an internal error.'
        else:
            embed.title = f'[✅ ({result.src} -> {result.dest})] '+message
        finally:
            await embed_id.edit(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Chat(bot))

