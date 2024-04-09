import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from dateutil import tz 
import asyncio


class Purge(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.x: dict = [f for f in self.bot.mongo.automod.find()][0]['automod_config']['auto_purge_config']

        self.channel_p = int(self.x.get("auto_purge_channel_id"))
        self.delay = int(self.x.get("auto_purge_delay"))

    
    @tasks.loop(seconds=5)
    async def update_purge_timer(self):

        nt = self.x.get("next_purge")

        if nt != "":

            current_time = datetime.now()
            iso = datetime.fromisoformat(str(nt))

            if iso < current_time or iso == current_time:
                channel = self.bot.get_channel(self.channel_p)
                
                try:

                    async for message in channel.history(limit=None, oldest_first=True):
                        await message.delete()
                        await asyncio.sleep(7.5)
                    
                    update = {
                        "next_purge": datetime.now() + timedelta(seconds=int(self.x.get("auto_purge_delay")))
                    }
                    x: dict = [f for f in self.bot.mongo.automod.find()][0]

                    x['automod_config']['auto_purge_config'].update(update)
                    self.bot.mongo.automod.update_one({"_id": x['_id']}, {"$set":{"automod_config":x['automod_config']}})

                    await channel.send("Auto Purge concluído com sucesso.")
                
                except Exception as e:
                    self.bot.log.info("Um erro aconteceu no módulo Auto Purge: %s", e)
        
            else:    
                current_time = datetime.now()
                update = {
                    "last_check": current_time
                }
                x: dict = [f for f in self.bot.mongo.automod.find()][0]

                x['automod_config']['auto_purge_config'].update(update)
                return self.bot.mongo.automod.update_one({"_id": x['_id']}, {"$set":{"automod_config":x['automod_config']}})
        
        else:

            current_time = datetime.now()
            update = {
                    "next_purge": current_time + timedelta(seconds=int(self.x.get("auto_purge_delay")))
                }
            x: dict = [f for f in self.bot.mongo.automod.find()][0]

            x['automod_config']['auto_purge_config'].update(update)
            return self.bot.mongo.automod.update_one({"_id": x['_id']}, {"$set":{"automod_config":x['automod_config']}})


    def _start(self):

        if self.x.get("auto_purge_id") != "":
            return self.update_purge_timer.start()
        else:
            return self.bot.log.warning("O módulo Auto Purge não está configurado, por isso sua ativação foi cancelada.")
        

async def setup(bot: commands.Bot):
    await bot.add_cog(Purge(bot))