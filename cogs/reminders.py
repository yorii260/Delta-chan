from datetime import datetime, timedelta, timezone
from typing import Any, Coroutine 
from discord.ext import commands, tasks 
from dateutil.tz import gettz
import discord 
from dateutil import parser


tzinfo = gettz('America/Sao_Paulo')

"""
reminder = {
    "user_id": "",
    "channel_id": 0,
    "reminder": "",
    "last_check": datetime.time,
    "in": datetime.time
}
"""


class Reminder(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot 

        self.update_reminders.start()
    
    @tasks.loop(seconds=10)
    async def update_reminders(self):
        
        all_reminds = [x for x in self.bot.mongo.users.find() if len(x['reminders']) > 0]
        
        if len(all_reminds) >= 1:
            
            for i in range(len(all_reminds)):
                
                if len(all_reminds[i]['reminders'][0].values()) >= 1:
                    user, channel, remind, in_, last_check = all_reminds[i]['reminders'][0].values()
                    print(user)
                    now = datetime.now()
                    
                    if now == in_ or now > datetime.fromisoformat(str(in_)):
                
                        r = self.bot.mongo.update_user(
                            int(user),
                            {
                                "$set": {
                                    "reminders": [{i: {}}]
                                }
                            }
                        )
                        
                        if r is not None:
                            self.bot.mongo.update_user(
                                int(user),
                                {
                                    "$inc": {
                                        "reminders_count":
                                            -1
                                    }
                                }
                            )
                        return await self.bot.dispatch("reminder_submit", self.bot.get_channel(int(channel)), self.bot.get_user(int(user)), remind)
                    
        else:
            return
    
    
    @commands.Cog.listener()
    async def on_reminder_submit(self, channel: discord.TextChannel, user: discord.User, remind: str):
        
        em = discord.Embed(title=f"{user.name} reminder", description=f"O seu lembrete está aqui!!\n\nLembrete: `{remind}`", color=0x800080)
        
        return await channel.send(embed=em, content=user.mention)
    
    
    def cog_unload(self):
        self.update_reminders.cancel()         
    

            
async def setup(bot: commands.Bot):
    await bot.add_cog(Reminder(bot))