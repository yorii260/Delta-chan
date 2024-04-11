import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from dateutil import tz 
import asyncio


class Purge(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot 
    

    async def getting_all_messages(self, channel: discord.TextChannel) -> list[discord.Message]:

        messages = []
        count = 1
        async for message in channel.history(limit=None, oldest_first=True):
            messages.append(message)

            count += 1
            await asyncio.sleep(3.5)

        self.bot.log.info("Fetching %s messages in %s.", len(messages), channel.name)
        
        return messages


    @tasks.loop(seconds=10)
    async def update_purge_time(self):

        purge_info: dict = [x for x in self.bot.mongo.automod.find()][0]

        auto_purge_id = purge_info['automod_config']['auto_purge_config'].get("auto_purge_id")
        next_purge = purge_info['automod_config']['auto_purge_config'].get("next_purge")
        delay = purge_info['automod_config']['auto_purge_config'].get("auto_purge_delay")
        auto_purge_channel = self.bot.get_channel(int(purge_info['automod_config']['auto_purge_config'].get("auto_purge_channel_id")))

        if auto_purge_id != "":
            
            purge_time = datetime.fromisoformat(str(next_purge))

            if purge_time < datetime.now() or purge_time == datetime.now():

                msgs = await self.getting_all_messages(auto_purge_channel)

                return self.bot.dispatch("purge_timeout", msgs, purge_info, delay)

            else:
                purge_info['automod_config']['auto_purge_config'].update({"last_check": datetime.now()})

                return self.bot.mongo.automod.update_one({"_id": purge_info.get("_id")}, {"$set":{"automod_config":purge_info['automod_config']}})
        else:
            self.bot.log.warning("Exiting Auto Purge process because the process is desactived.")
            self.update_purge_time.cancel()
        

    @update_purge_time.before_loop
    async def before_purge(self):
        await self.bot.wait_until_ready()


    @commands.Cog.listener()
    async def on_purge_timeout(self, msgs: list[discord.Message], purge_info: dict, delay: int):

        msg_count = len(msgs)
        count = 1 

        try:
            
            if msg_count != 0:

                for msg in msgs:
                    await msg.delete()

                    self.bot.log.info("Purge Process: Deleted %s/%s messages.", count, msg_count)
                    count +=1

                    del msgs[msgs.index(msg)]
                    await asyncio.sleep(2.5)
                
                update = {
                    "next_purge": datetime.now() + timedelta(seconds=int(delay))
                }
                purge_info['automod_config']['auto_purge_config'].update(update)
                return self.bot.mongo.automod.update_one({"_id": purge_info['_id']}, {"$set":{"automod_config":purge_info['automod_config']}})

            else:
                return self.bot.log.info("O chat atual não possuí nenhuma mensagem, skipped.")
            
            
        except Exception as e:
            self.bot.log.warning("Um erro ocorreu: %s", e)


async def setup(bot: commands.Bot):
    await bot.add_cog(Purge(bot))