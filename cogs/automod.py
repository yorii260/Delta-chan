from discord.ext import commands 
import discord
from datetime import datetime
from pymongo.collection import Collection
from src.views.automod_views import AutomodView 

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
    def filter(self) -> str:
        return self.config.get("auto_delete_filter")
    
    @property
    def type(self) -> str:
        return self.config.get("auto_delete_type")


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
    

async def setup(bot: commands.Bot):
    await bot.add_cog(AutomodCog(bot))
