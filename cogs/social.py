from discord.ext import commands 
import discord 
import typing 
from src.views.SocialViews import UiView


class SocialCommands(commands.Cog, name="Social"):
    
    """
    Todos os comandos relacionados à uso geral estará presente aqui.
    
    """
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
    
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.command(
        name = 'userinfo',
        description = "`Informações sobre você ou um usuário qualquer.`",
        aliases = ('ui',),
        usage=f"d.userinfo <user id or user_mention>"
    )
    async def infouser(self,
                       ctx: commands.Context,
                       user: discord.Member = None):
        
        if user is None:
            user = ctx.author 
            
        if user == self.bot.user:
            return
        
        
        embed = discord.Embed(
            title=user.name, 
            color=0x800080
        )
        
        embed.set_thumbnail(url=user.avatar.url)
        
        embed.add_field(name="ID",
                        value=f"`{user.id}`",
                        inline=True)

        embed.add_field(name="Entrou há",
                        value=f"<t:{int(user.joined_at.timestamp())}:f>"
                    )
        
        
        return await ctx.reply(embed=embed, view=UiView(user=user, ctx=ctx))


async def setup(bot: commands.Bot):
    await bot.add_cog(SocialCommands(bot))