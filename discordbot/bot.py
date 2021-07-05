import discord
from discord.ext import commands

import logging
logger = logging.getLogger('__main__')

class ShowcaseBot(commands.Bot):

    COGS = [
        'discordbot.cogs.main',
        'discordbot.cogs.showtime'
    ]

    def __init__(self, prefix, token):
        self.BOT_PREFIX = prefix
        self.TOKEN = token
        super().__init__(command_prefix=prefix, description="Showcase management Discord bot")
        
        for cog in self.COGS:
            try:
                self.load_extension(cog)
            except Exception as e:
                raise Exception("Failed to load cog {}".format(cog))

    async def on_ready(self):
        printString = "\nLogged in as:" + "\n"
        printString += "Username: " + self.user.name + "#" + self.user.discriminator + "\n"
        printString += "ID: " + str(self.user.id) + "\n\n"
        printString += "Connected to servers: " + "\n"
        guilds = await self.fetch_guilds(limit=100).flatten()
        for guild in guilds:
            printString += "*" + guild.name + "\n"
        
        logger.info(printString)

        await self.change_presence(status=discord.Status.online, activity=discord.Game("Showcasing cool projects 🕶"))
    
    def run(self):
        super().run(self.TOKEN, reconnect=True)