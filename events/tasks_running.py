import discord
from discord.ext import commands, tasks
import cogs as c 
from datetime import datetime, timedelta
import asyncio


class RunningTasks(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot 

        self.update_reminders.start()
        self.update_purge_time.start()
    

    @tasks.loop(seconds=5)
    async def update_reminders(self):
        
        try:
            all_reminds = [x for x in self.bot.mongo.reminders.find()]
            
            current_time = datetime.now() 
            
            for reminder in all_reminds:
                
                user, channel, remind, date, last_check = reminder['reminder'].values()
                id_ = reminder['_id']
                date = datetime.fromisoformat(str(date))
            
                if date < current_time or date == current_time:
                    
                    self.bot.dispatch('reminder_timeout', user, channel, remind, id_)
                else:
                    self.bot.mongo.reminders.replace_one({"_id": id_}, {"_id": id_, "reminder": {"user_id": user,
                                                                                                            "channel_id": channel,
                                                                                                            "remind": remind,
                                                                                                            "in": date,
                                                                                                            "last_check": current_time}})
        except Exception as e:
            self.bot.log.warning(e)
    
    
    @update_reminders.before_loop
    async def before_update_reminders(self):
        await self.bot.wait_until_ready()
    

    @tasks.loop(seconds=10)
    async def update_purge_time(self):

        auto_purge_id = self.bot.auto_purge.id_
        next_purge = self.bot.auto_purge.next_purge
        delay = self.bot.auto_purge.delay
        auto_purge_channel = self.bot.auto_purge.channel

        if auto_purge_id is not None and next_purge is not None:
            
            purge_time = datetime.fromisoformat(str(next_purge))

            if purge_time < datetime.now() or purge_time == datetime.now():

                msgs = await self.getting_all_messages(auto_purge_channel)

                if len(msgs) > 0:
                    return self.bot.dispatch("purge_timeout", msgs, delay)
                
            else:
                x = [x for x in self.bot.mongo.automod.find()][0]

                x['automod_config']['auto_purge_config'].update({"last_check": datetime.now()})

                return self.bot.mongo.automod.update_one({"_id": x.get("_id")}, {"$set":{"automod_config":x['automod_config']}})
        else:
            self.bot.log.warning("Exiting Auto Purge process because the process is desactived.")
            
            if self.update_purge_time._can_be_cancelled():
                return self.update_purge_time.cancel()
    

    async def getting_all_messages(self, channel: discord.TextChannel) -> list[discord.Message]:

        messages = []
        count = 1
        async for message in channel.history(limit=None, oldest_first=True):
            messages.append(message)

            count += 1
            await asyncio.sleep(3.5)

        self.bot.log.info("Fetching %s messages in %s.", len(messages), channel.name)
        
        return messages
    

    @update_purge_time.before_loop
    async def before_purge(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(RunningTasks(bot))