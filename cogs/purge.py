import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from dateutil import tz 


class Purge(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.x: dict = [f for f in self.bot.mongo.automod.find()][0]['automod_config']['auto_purge_config']

        self.channel_p = int(self.x.get("auto_purge_channel_id"))
        self.delay = int(self.x.get("auto_purge_delay"))

    
    async def update_purge_timer(self):

        nt = self.x.get("next_purge")

        if nt != "":

            current_time = datetime.now(tz=tz.gettz("America/Sao_Paulo"))
            iso = datetime.fromisoformat(str(nt))

            if current_time >= iso:

                async for history in self.bot.get_channel(self.channel_p).history(limit=None):
                    await history.delete()
            
        else:
            return



    