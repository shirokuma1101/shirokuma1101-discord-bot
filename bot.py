# coding: utf-8

# standard
import argparse
import configparser
import os

# discord
import discord
from discord.ext import commands


# cogs
EXTENSIONS = [
    'cogs.chat',
]

class Bot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        for extension in EXTENSIONS:
            try:
                await self.load_extension(extension)
            except Exception as e:
                print(f'Failed to load extension {extension}.: {e}')

        await self.tree.sync()


def main():

    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='bot.ini', type=str, help='config file')
    args = parser.parse_args()

    # check args
    if not os.path.exists(args.config):
        print(f'config file not found: {args.config}')
        exit(1)

    # read config
    config = configparser.ConfigParser()
    config.read(args.config)
    discord_token = config['SETTING']['token']

    # setup intents
    intents = discord.Intents.default()
    intents.members = True

    # run bot
    bot = Bot(
        command_prefix='/',
        help_command=commands.MinimalHelpCommand(),
        intents=intents,
        activity=discord.Activity(type=discord.ActivityType.listening, name='Type /Help'),
        case_insensitive=True)
    bot.run(discord_token)


if __name__ == "__main__":
    main()

