import discord
from discord.ext import commands 
import cogs as c 
from datetime import datetime, timedelta
import asyncio


class GeralEventListener(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot 


    @commands.Cog.listener()
    async def on_reminder_timeout(self, user, channel, remind, id_):
        
        user = self.bot.get_user(int(user))
        channel = self.bot.get_channel(int(channel))
        
        embed = discord.Embed(title=f"{user} reminder", description=f"Seu reminder chegou!!!\nReminder: `{remind}`", color=0x800080)
        
        await channel.send(embed=embed, content=user.mention)
        
        self.bot.log.info("Reminder disptach has been received and sended to user %s", user.name)
        return self.bot.mongo.reminders.delete_one({"_id": id_})


    @commands.Cog.listener('on_message')
    async def check_or_remove_afk(self, message: discord.Message):
    
        g = [f for f in self.bot.mongo.afk.find()]
        
        for x in range(0, len(g)):
            
            id_, user, guild, reason, afk_date = g[x].values()
            
            if message.guild != None and message.guild.id == guild and not message.author.bot:
                
                if message.author.id == user and not message.content.startswith(self.bot.command_prefix):
                    self.bot.mongo.afk.delete_one({"_id": id_})
                    return await message.reply(f"<@{user}>, o seu AFK foi removido.")
                
                elif message.author.id != user and user in [f.id for f in message.mentions]:
                    return await message.reply(f"<@{user}> está AFK com o motivo: `{reason.strip()}` {afk_date[0]}.")
                else:
                    pass
    

    @commands.Cog.listener()
    async def on_warn_submit(self, warned_user: discord.Member, moderator_user: discord.Member, reason: str):
        
        channel = self.bot.mongo.audit_channel()

        if channel is None:
            return 
        
        channel = self.bot.get_channel(int(channel))
        
        em = discord.Embed(title=f"{warned_user.name} recebu um aviso.", description=f"**Moderador**: {moderator_user.mention}\n**Motivo**: `{reason}`",
                           color=0x800080)
        em.set_thumbnail(url=warned_user.avatar.url)
        
        return await channel.send(embed=em)


    @commands.Cog.listener()
    async def on_purge_timeout(self, msgs: list[discord.Message], delay: int):

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

                x = [x for x in self.bot.mongo.automod.find()][0]
                x['automod_config']['auto_purge_config'].update(update)
                return self.bot.mongo.automod.update_one({"_id": x['_id']}, {"$set":{"automod_config":x['automod_config']}})

            else:

                update = {
                    "next_purge": datetime.now() + timedelta(seconds=int(delay))
                }
                x = [x for x in self.bot.mongo.automod.find()][0]
                x['automod_config']['auto_purge_config'].update(update)
                self.bot.mongo.automod.update_one({"_id": x['_id']}, {"$set":{"automod_config":x['automod_config']}})
                
                return self.bot.log.info("O chat atual não possuí nenhuma mensagem, skipped.")            

        except Exception as e:
            self.bot.log.warning("Um erro ocorreu: %s", e)
    

async def setup(bot: commands.Bot):
    await bot.add_cog(GeralEventListener(bot))

"""

"""