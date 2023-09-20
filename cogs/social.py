from discord.ext import commands 
import discord 
import typing 


class SocialCommands(commands.Cog, name="Social"):
    
    """
    Todos os comandos relacionados à uso geral estará presente aqui.
    
    """
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
    
    
    @commands.command(
        name = 'userinfo',
        description = "`Informações sobre você ou um usuário qualquer.`",
        aliases = ('ui',),
        usage=f"d.userinfo <user id or user_mention>"
    )
    async def infouser(self,
                       ctx: commands.Context,
                       user: typing.Union[discord.User, discord.Member] = None):
        
        if user is None:
            user = ctx.author 
        
        
        embed = discord.Embed(
            title=user.name, 
            color=0x800080
        )
        
        embed.set_thumbnail(url=user.avatar.url)
        
        embed.add_field(name="ID",
                        value=f"`{user.id}`",
                        inline=True)

        embed.add_field(name="Joined at",
                        value=user.joined_at.strftime('%d/%m/%Y às %H:%M'))
        return await ctx.reply(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(SocialCommands(bot))