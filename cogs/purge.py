import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from dateutil import tz 
import asyncio


class Purge(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.x: dict = [f for f in self.bot.mongo.automod.find()][0]['automod_config']['auto_purge_config']

        self.channel = int(self.x.get("auto_purge_channel_id"))
        self.delay = int(self.x.get("auto_purge_delay"))

    
    @tasks.loop(seconds=30)
    async def update_purge_timer(self):

        nt = self.x.get("next_purge")
        channel = self.bot.get_channel(self.channel)


        if nt != "":

            current_time = datetime.now()
            iso = datetime.fromisoformat(str(nt))

            if iso <= datetime.now():
                
                self.bot.log.info("Starting Auto Purge process.")
                
                try:
                    
                    messages = []
                    async for message in channel.history(limit=None):
                        messages.append(message) 
                    
                    else:

                        self.bot.log.info("%s messages has been encountered in the current chat.", len(messages))
                        await channel.delete_messages(messages,
                                                      reason=f"Auto Purge | {self.bot.user.id}")
                        
                        update = {
                            "next_purge": datetime.now() + timedelta(seconds=int(self.x.get("auto_purge_delay")))
                        }
                        x: dict = [f for f in self.bot.mongo.automod.find()][0]
                        x['automod_config']['auto_purge_config'].update(update)
                        
                        self.bot.mongo.automod.update_one({"_id": x['_id']}, {"$set":{"automod_config":x['automod_config']}})
                        
                
                except Exception as e:
                    return self.bot.log.info("Um erro aconteceu no módulo Auto Purge: %s", e)
                
                return await channel.send(f"Auto Purge concluído com sucesso.\nPróximo purge será daqui <t:{int(iso.timestamp())}:R>") 
        
        
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
            self.bot.log.info("Starting Auto Purge looping process.")

            if not self.update_purge_timer.is_running():
                return self.update_purge_timer.start()
        else:
            return self.bot.log.warning("O módulo Auto Purge não está configurado, por isso sua ativação foi cancelada.")
        

async def setup(bot: commands.Bot):
    await bot.add_cog(Purge(bot))