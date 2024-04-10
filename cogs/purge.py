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

            self.bot.log.info("%s message%s", count, "s" if count > 1 else "")
        
        return messages


    @tasks.loop(seconds=10)
    async def update_purge_time(self):

        purge_info = [x for x in self.bot.mongo.automod.find()][0]['automod_config']['auto_purge_config']

        auto_purge_id, auto_purge_channel_id, auto_purge_delay, auto_purge_guild_id, next_purge, last_check = purge_info.values()

        if auto_purge_id != "":
            
            purge_time = datetime.fromisoformat(str(next_purge))

            if purge_time < datetime.now() or purge_time == datetime.now():

                msgs = await self.getting_all_messages()

                return self.bot.dispatch("purge_timeout", msgs, purge_info)
        else:
            self.update_purge_time.cancel()
        

    @update_purge_time.before_loop
    async def before_purge(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Purge(bot))