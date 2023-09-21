from discord.ext import commands 
import discord
from datetime import timedelta, datetime
from src.views.moderation_views import BanView


class Moderation(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
    
    
    @commands.has_guild_permissions(
        ban_members=True
    )
    @commands.guild_only()
    @commands.command(name='ban',
                      description='Banir um membro do servidor permanentemente.',
                      usage='d.ban [user] <time> [reason]',
                      aliases=('bn', 'banir',))
    async def ban_member(self,
                         ctx: commands.Context,
                         user: discord.Member,
                         *,
                         reason: str):
        
        em = discord.Embed(color=0x800080, title=f"Ban confirmation",
                           description=f"Você tem certeza que deseja banir o membro `{user.name}`?\n\nO banimento dele será permanentemente!\nMotivo: `{reason}`")
        
        return await ctx.reply(embed=em,
                               view=BanView(data=[user, reason]))
        

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))