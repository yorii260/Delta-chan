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
        
        self.warns = self.db.get_collection('GUILD_WARNS')
        self.bans = self.db.get_collection("GUILD_BANS")
        self.users = self.db.get_collection("GUILD_USERS")
    
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        
        if message.author.bot: 
            return 
        elif message.guild.id != int(os.getenv("guild_id")):
            return
        else:
            
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
    
    
    def find_user(self, user: discord.Member):
        
        check = self.users.find_one({
            "id_": user.id
        })
        
        return check 

    
    def insert_warn(self, user: discord.Member, moderator: discord.Member, reason: str):
        
        r = self.warns.insert_one(({
            "id_": user.id,
            "warn_id": utils.random_id(),
            "date": utils.now_time(),
            "moderator_id": moderator.id,
            "motivo": reason
        }))
        
        return r.inserted_id 

    
    def list_warns(self, user: discord.Member):
        
        user_ = [x for x in self.warns.find() if x['id_'] == user.id]
        
        msg = ''
        if user_ is not None:
            
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


async def setup(bot: commands.Bot):
    await bot.add_cog(Mongo(bot))
            