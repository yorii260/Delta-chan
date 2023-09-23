from datetime import datetime, timedelta, timezone
from typing import Any, Coroutine 
from discord.ext import commands, tasks 
from dateutil.tz import gettz
import asyncio
import discord


class Reminder(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
    
    
    @tasks.loop(seconds=5)
    async def update_reminders(self):
        
        all_reminds = [x for x in self.bot.mongo.reminders.find()]
        
        current_time = datetime.now() 
        
        for reminder in all_reminds:
            
            user, channel, remind, date, last_check = reminder['reminder'].values()
            id_ = reminder['_id']
            date = datetime.fromisoformat(str(date))
           
            if date < current_time or date == current_time:
                
                return self.bot.dispatch('reminder_timeout', user, channel, remind, id_)
            else:
                self.bot.mongo.reminders.replace_one({"_id": id_}, {"_id": id_, "reminder": {"user_id": user,
                                                                                                           "channel_id": channel,
                                                                                                           "remind": remind,
                                                                                                           "in": date,
                                                                                                           "last_check": current_time}})
    
    
    @update_reminders.before_loop
    async def before_update_reminders(self):
        await self.bot.wait_until_ready()
    
    
    @commands.Cog.listener()
    async def on_reminder_timeout(self, user, channel, remind, id_):
        
        user = self.bot.get_user(int(user))
        channel = self.bot.get_channel(int(channel))
        
        embed = discord.Embed(title=f"{user} reminder", description=f"Seu reminder chegou!!!\nReminder: `{remind}`", color=0x800080)
        
        await channel.send(embed=embed, content=user.mention)
        
        return self.bot.mongo.reminders.delete_one({"_id": id_})
        
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Reminder(bot))