"""
Automod - DeltaChan

- Auto Delete
- Kick New Account
- Auto Ban
- Auto Purge

"""

from discord.ext import commands 
import discord
from datetime import datetime
from pymongo.collection import Collection
from src.views.automod_views import AutomodView, AutomodConfigView


class Automod:

    def __init__(self, bot: commands.Bot):
        self.bot = bot 

    @property
    def collection(self) -> Collection:
        return self.bot.mongo.automod
    

class AutoDelete(Automod):

    def __init__(self, bot: commands.Bot):
        self.bot = bot 

    
    @property 
    def config(self) -> dict:
        return [x for x in self.collection.find()][0]['automod_config']['auto_delete_config']
    
    @property
    def id_(self) -> dict | None:
        return self.config.get("auto_delete_id") if self.config.get("auto_delete_id") != "" else None
    
    @property
    def channel(self) -> discord.TextChannel | None:
        channel = self.bot.get_channel(int(self.config.get("auto_delete_channel_id")))

        if channel is not None:
            return channel
        else:
            return None 
    
    @property
    def filter(self) -> str | None:

        fil = self.config.get("auto_delete_filter").strip()

        if len(fil) > 0: return fil.split(":")[1]
        else: return None
    
    @property
    def punish(self) -> any:
        return self.config.get("auto_delete_punish")


    def update(self, update: dict):
        x = [x for x in self.collection.find()][0]
        x['automod_config']['auto_delete_config'].update(update)
        result = self.collection.update_one({"_id": x['_id']}, {"$set":{"automod_config":x['automod_config']}})

        return result.upserted_id
        
    

class AutoPurge(Automod):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @property 
    def config(self) -> dict:
        return [x for x in self.collection.find()][0]['automod_config']['auto_purge_config']
    
    @property
    def id_(self) -> str | None:
        return self.config.get("auto_purge_id") if self.config.get("auto_purge_id") != "" else None
    
    @property
    def channel(self) -> discord.TextChannel | None:
        channel = self.bot.get_channel(int(self.config.get("auto_purge_channel_id")))

        if channel is not None:
            return channel
        else:
            return None 
    
    @property
    def next_purge(self) -> datetime | None:
        date = datetime.fromisoformat(str(self.config.get("next_purge")))
        
        if date != "": return date 
        else: return None 
    
    @property
    def last_check(self) -> datetime | None:
        lc = datetime.fromisoformat(str(self.config.get("last_check")))

        if lc != "": return lc 
        else: return None
    
    @property
    def delay(self) -> int:
        return int(self.config.get("auto_purge_delay"))
    
    def update(self, update: dict):
        x = [x for x in self.collection.find()][0]
        x['automod_config']['auto_purge_config'].update(update)
        result = self.collection.update_one({"_id": x['_id']}, {"$set":{"automod_config":x['automod_config']}})

        return result.upserted_id


class AutomodCog(commands.Cog, name="Automod"):
    
    def __init__(self, bot: commands.Bot):
        
        self.bot = bot
    
    
    @commands.Cog.listener('on_message')
    async def automod_auto_delete(self, message: discord.Message):
    
        # /////////////////////////////////////////////// # 
        
        ad_id = self.bot.auto_delete.id_

        if ad_id is not None:

            filter = self.bot.auto_delete.filter
            punish = self.bot.auto_delete.punish
            channel = self.bot.auto_delete.channel
            

            if (
                not message.author.bot and 
                message.channel.id == channel.id
            ):
                if filter != 'default':
                    
                    filter=filter.strip().split(':')
                    
                    if filter[0] == "SW":
                        filter = message.content.lower().strip().startswith(filter[1].strip().lower())
                    elif filter[0] == "EW":
                        filter = message.content.strip().lower().endswith(filter[1].strip().lower())
                    
                    
                else:
                    filter = True 

                if filter:
                
                    return await message.delete()

        else:
            return 
    
    @commands.group(
        name='automod',
        description='Comandos relacionados à moderação automática.',
        usage='d.automod',
        aliases=("a",)
    )
    async def auto(self, ctx: commands.Context):
        pass 
        
    @auto.command(name='painel', hidden=True)
    async def painel(self, ctx: commands.Context):
        embed = discord.Embed(
            title='Automod Painel',
            color=0x800080,
            description='Veja as configurações atuais de cada módulo.'
        )
        
        embed.set_thumbnail(url=ctx.author.avatar.url)
        await ctx.send(embed=embed, view=AutomodView(self.bot))

    
    @auto.command(
        name='config',
        description = "Veja e modifique as configurações de todos os módulos.",
        usage = 'd.automod config',
        aliases=("cf",)
    )
    async def cf(self, ctx: commands.Context):
        
        embed = discord.Embed(title='Automod Config', color=0xff0000)
        embed.description = "Veja as atuais configurações do atual servidor."
        return await ctx.send(embed=embed, view=AutomodConfigView(self.bot))
    

async def setup(bot: commands.Bot):
    await bot.add_cog(AutomodCog(bot))
