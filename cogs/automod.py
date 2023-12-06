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
import random 
from pymongo.collection import Collection


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
    
    def __init__(self, bot: commands.Bot, database: Collection):
        
        self.bot = bot
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
                raise AutomodException(f"O role `{roles.id}` has already in the database, skipped.")
            ammr['automod_moderator_roles'].append(roles.id)
            return self.data.update_one({"_id": self._id}, {"$set": {"automod_config":ammr}}, upsert=True)
    
    
    def update_ignored_roles(self, roles: discord.Role | list[discord.Role]):
        
        ammr = self.dict[0]['automod_config']
        
        if type(roles) == list and len(roles) > 1:
            
            for role in roles:
                
                if role.id in ammr['automod_ignored_roles']:
                    raise AutomodException(f"O role {role.id} has already in the database, skipped.")

                ammr['automod_ignored_roles'].append(role.id)
                
            return self.data.update_one({"_id": self._id}, {"$set": {"automod_config":ammr}})
        else:
            
            if roles.id in ammr['automod_ignored_roles']:
                raise AutomodException(f"O role {roles.id} has already in the database, skipped.")
            ammr['automod_ignored_roles'].append(roles.id)
            return self.data.update_one({"_id": self._id}, {"$set": {"automod_config":ammr}}, upsert=True)
    
    
    def update_auto_delete(self, update):
        
        d: dict = self.dict[0]['automod_config']
        d['auto_delete_config'].update(update)
        
        return self.data.update_one({"_id": self._id}, {"$set":{"automod_config":d}})

class AutomodCog(commands.Cog, name="Automod"):
    
    def __init__(self, bot: commands.Bot):
        
        self.bot = bot
        self.log = self.bot.log 
        
        self.automod_ = AutomodDatabase(self.bot, self.bot.mongo.automod)
    
    
    @commands.group(name='automod',
                    description='Comandos relacionados ao AutoMod.')
    async def automod(self, ctx: commands.Context):
        pass 
    
    @automod.command(name='add_moderator_role',
                     aliases=('amr',))
    async def _(self, ctx: commands.Context, *, role: discord.Role):
        self.automod_.update_moderator_roles(role)
        return await ctx.send(f"`{role.name}` foi adicionado com sucesso.")
    
    
    @automod.command(name='add_ad_filter',
                     aliases=('adf',))
    async def _(self, ctx: commands.Context, *, filter: str):
        d = {
            "auto_delete_id": random.randint(0, 99999),
            "auto_delete_channel_id": ctx.channel.id,
            "auto_delete_filter": filter,
            "auto_delete_punish": "Ban"
        }
        self.automod_.update_auto_delete(d)
        return await ctx.send("Update sucessfull.")


async def setup(bot: commands.Bot):
    await bot.add_cog(AutomodCog(bot))