"""
Automod - DeltaChan

- Auto Delete
- Kick New Account
- Auto Ban
- Auto Purge

"""

from discord.ext import commands 
from helpers import utils 
import discord
from datetime import timedelta, datetime
from pymongo.collection import Collection
from dateutil import tz
from src.views.automod_views import AutomodView, AutomodConfigView
from discord.ext import tasks

automod_config = {
    
    "automod_moderator_roles": [],
    "automod_ignored_roles": [],
    
    "auto_delete_config": {
        "auto_delete_id": "",
        "auto_delete_channel.id": "",
        "auto_delete_filter": "",
        "auto_delete_punish": ""
    },
    "auto_ban_config": {
        "auto_ban_guild.id": "",
        "auto_ban_id": "", 
        "auto_ban_when": "",
        "auto_ban_ignored.channels": [],
        "auto_ban_ignored.roles": []
    },
    "auto_purge_config": {
        "auto_purge_id": "",
        "auto_purge_channel.id": "",
        "auto_purge_delay": "",
        "auto_purge_guild.id": ""
    },
    "kick_new_account.config": {
        "kick_id": "",
        "kick_guild_id": "",
        "kick_minimum_time": ""
    }
}

class AutomodException(commands.CheckFailure):
    
    def __init__(self, message: str, *args):
        super().__init__(message, *args)
        self.message = message 
        
        
class AutomodDatabase:
    
    def __init__(self, database: Collection):
        
        self.data = database
        self.dict = [f for f in self.data.find()]
        self._id = self.dict[0]['_id']
    
    
    def update_moderator_roles(self, roles: discord.Role | list[discord.Role]):
        
        ammr = self.dict[0]['automod_config']
        
        if type(roles) == list and len(roles) > 1:
            
            for role in roles:
                
                if role.id in ammr['automod_moderator_roles']:
                    raise AutomodException(f"O role `{role.id}` has already in the database, skipped.")

                ammr['automod_moderator_roles'].append(role.id)
                
            return self.data.update_one({"_id": self._id}, {"$set": {"automod_config":ammr}})
        else:
            
            if roles.id in ammr['automod_moderator_roles']:
                raise AutomodException(f"O cargo {role.mention if role.mentionable else role.id} já está na database.")
            ammr['automod_moderator_roles'].append(roles.id)
            return self.data.update_one({"_id": self._id}, {"$set": {"automod_config":ammr}}, upsert=True)
    
    
    def update_ignored_roles(self, roles: discord.Role | list[discord.Role]):
        
        ammr = self.dict[0]['automod_config']
        
        if type(roles) == list and len(roles) > 1:
            
            for role in roles:
                
                if role.id in ammr['automod_ignored_roles']:
                    raise AutomodException(f"O cargo {role.mention if role.mentionable else role.id} já está na database.")

                ammr['automod_ignored_roles'].append(role.id)
                
            return self.data.update_one({"_id": self._id}, {"$set": {"automod_config":ammr}})
        else:
            
            if roles.id in ammr['automod_ignored_roles']:
                raise AutomodException(f"O cargo {roles.mention if roles.mentionable else roles.id} já está na database.")
            ammr['automod_ignored_roles'].append(roles.id)
            return self.data.update_one({"_id": self._id}, {"$set": {"automod_config":ammr}}, upsert=True)
    
    
    def update_auto_delete(self, update):
        
        d: dict = self.dict[0]['automod_config']
        d['auto_delete_config'].update(update)
        
        return self.data.update_one({"_id": self._id}, {"$set":{"automod_config":d}})

    
    def update_auto_ban(self, update):
        
        d: dict = self.dict[0]['automod_config']
        d['auto_ban_config'].update(update)
        
        return self.data.update_one({"_id": self._id}, {"$set":{"automod_config":d}})
    
    
    def update_auto_purge(self, update):
        
        d: dict = self.dict[0]['automod_config']
        d['auto_purge_config'].update(update)
        
        return self.data.update_one({"_id": self._id}, {"$set":{"automod_config":d}})

    
    def update_kick_new_account(self, update):
        
        d: dict = self.dict[0]['automod_config']
        d['kick_new_account_config'].update(update)
        
        return self.data.update_one({"_id": self._id}, {"$set":{"automod_config":d}})
    
    
class AutomodCog(commands.Cog, name="Automod"):
    
    def __init__(self, bot: commands.Bot):
        
        self.bot = bot
        self.log = self.bot.log 
        
        self.automod_ = AutomodDatabase(self.bot.mongo.automod)
    
    
    @commands.Cog.listener('on_message')
    async def automod_auto_delete(self, message: discord.Message):
        
        config = self.automod_.dict[0]['automod_config']['auto_delete_config']
        
        # /////////////////////////////////////////////// # 
        
        ad_id = config['auto_delete_id']

        if ad_id != "":
            filter = config['auto_delete_filter']
            punish = config['auto_delete_punish']
            channel = int(config['auto_delete_channel_id'])
            

            if (
                not message.author.bot and 
                message.channel.id == channel
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
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        
        config = self.automod_.kick_new_account
        minimum_time = config[2]
        log_channel = self.bot.get_channel(self.bot.mongo.audit_channel)
        
        
        time = datetime.now(tz=tz.UTC) + timedelta(days=int(minimum_time))
        user_time = member.created_at.astimezone(tz=tz.UTC)
        
        if time > user_time or time == user_time:
            return await member.kick(reason="Filtro de contas fakes ativo!")


    @commands.group(
        name='automod',
        description='Comandos relacionados à moderação automática.',
        usage='d.automod',
        aliases=("a",)
    )
    async def auto(self, ctx: commands.Context):
        pass 
        
    @auto.command(name='painel')
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
