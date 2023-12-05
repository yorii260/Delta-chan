import pymongo
import discord
from discord.ext import commands 
import os
from helpers import utils
import re

class Mongo(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
        self.client = pymongo.MongoClient(os.getenv('MONGO_URL'))
        self.db = self.client.get_database('Delta')
           
        
    @property
    def users(self):
        return self.db.get_collection("GUILD_USERS")

    
    @property
    def warns(self):
        return self.db.get_collection('GUILD_WARNS')
    
    
    @property
    def bans(self):
        return self.db.get_collection("GUILD_BANS")
    
    
    @property
    def guild(self):
        return self.db.get_collection("GUILD_CONFIG")
    
    
    @property
    def reminders(self):
        return self.db.get_collection("REMINDERS")

    
    @property
    def afk(self):
        return self.db.get_collection('AFK')
    

    
    @property
    def automod(self):
        return self.db.get_collection('AUTOMOD_CONFIG')
    
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        
        if message.author.bot: 
            return 
        elif message.guild.id != int(os.getenv("guild_id")):
            return
        else:
            
            if (message.content.strip()[:1] == self.bot.command_prefix):
                
                user = self.bot.get_user(message.author.id)
                
                check = self.users.find_one({"id_": user.id})
                
                if check is None:
                    return self.users.insert_one({
                        "id_": user.id, 
                        "nickname": user.name, 
                        "avatar_url": user.avatar.url
                    })
                    
                else:
                    return
            
    
    async def insert_warn(self, user: discord.Member, guild_id: int, moderator: discord.Member, reason: str):
        
        self.warns.insert_one(({
            "id_": user.id,
            "warn_id": utils.random_id(),
            "guild_id": guild_id,
            "date": utils.now_time(),
            "moderator_id": moderator.id,
            "motivo": reason
        }))
        self.bot.dispatch("warn_submit", user, moderator, reason)
        
        return True

    
    def list_warns(self, user: discord.Member):
        
        user_ = [x for x in self.warns.find() if x['id_'] == user.id]
        
        msg = ''
        if len(user_) != 0:
            
            for i in user_:
                
                for key, item in i.items():
                    
                    if key != 'id_' and key != '_id':
                        
                        if key  == 'warn_id':
                            msg += f"`{item}` "
                        
                        elif key == 'date':
                            msg += f"- <t:{item}:f>\n"
                        elif key == 'moderator_id':
                            msg += f"**Moderador**: <@{item}> | `{item}`\n"
                        elif key == 'motivo':
                            msg += f"**Motivo**: `{item}`\n\n"
            
            return(msg)
        else:
            return None
    
    
    def audit_channel(self):
        
        data = [x for x in self.guild.find()]
        
        if len(data) > 0:
            
            return int(data[0]['audit_log_channel_id'])
        
        else:
            return None
    

    
    def update_audit_channel(self, channel: discord.TextChannel):
        data = self.guild.find()
        
        data.collection.update_one({}, {"$set": {"audit_log_channel_id": channel.id}})
        
        return data

    
    def delete_warn(self, warn_id: str):
        return self.warns.find_one_and_delete({"warn_id": warn_id})
      

async def setup(bot: commands.Bot):
    await bot.add_cog(Mongo(bot))
            