from discord.ext import commands 
import discord
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
                      usage='d.ban [user] <reason>',
                      aliases=('bn', 'banir',))
    async def ban_member(self,
                         ctx: commands.Context,
                         user: discord.Member,
                         *,
                         reason: str):
        
        em = discord.Embed(color=0x800080, title=f"Ban confirmation",
                           description=f"Você tem certeza que deseja banir o membro `{user.name}`?\n\nO banimento dele será permanentemente!\nMotivo: `{reason}`")
        
        return await ctx.reply(embed=em,
                               view=BanView(data=[user, ctx, reason]))
    
    @commands.has_guild_permissions(
        kick_members=True
    )
    @commands.guild_only()
    @commands.command(
        name='warn',
        description= 'Aplique um aviso a algum membro do servidor.',
        usage='d.warn <user> <motivo>',
        aliases=("aviso", 'avisar',)
    )
    async def warn(self, ctx: commands.Context, user: discord.Member, *, reason: str = 'Não informado'):
        """
        Warn command
        """
            
        em = discord.Embed(color=0x800080, title=f"{user.name} foi avisado!", description=f"**Moderator**: {ctx.author.mention}\n**Motivo**: `{reason}`")
        em.set_thumbnail(url=user.avatar.url)
        
        await ctx.reply(embed=em)
        return self.bot.mongo.insert_warn(user, ctx.author, reason)
    
    
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    @commands.command(
        name='list_warns',
        description="Veja os warns que algum usuário de seu servidor tem.",
        usage="d.list_warns <user>",
        aliases=("lw",)
    )
    async def list_warns(self, ctx: commands.Context, user: discord.Member):
        
        user_ = self.bot.mongo.list_warns(user)
        
        em = discord.Embed(title=f"{user.name} Warns", description=user_ if user_ is not None else "Nada.", color=0x800080)
        em.set_thumbnail(url=user.avatar.url)
        return await ctx.send(embed=em)
        
    
async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))