from discord.ext import commands 
import discord 
import typing


class HelpCog(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
        
    
    @commands.command(
        name='help',
        description='Veja todos os meus comandos disponíveis.',
        usage="teste"
    )
    async def ajuda(self, ctx: commands.Context, command_name: str = None):
        
        if command_name is None:
            
            embed = discord.Embed(title="My commands", description=f"Use `{self.bot.command_prefix}help <command_name>` para obter informações adicionais sobre tal comando.",color=0x800080)
            
            for cog in self.bot.cogs:
                
                text = ""
                for command in self.bot.get_cog(cog).get_commands():
                    text += f"`{command.name}`"
            
                embed.add_field(name=self.bot.get_cog(cog).qualified_name, value=text, inline=True)
            
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            
            return await ctx.reply(embed=embed)

        command = self.bot.get_command(command_name)
        
        if command is None:
            return await ctx.send(f"`{command_name}` não é um comando válido.")

        
        embed = discord.Embed(title=command.name, description=f"**Description**: `{command.description}`\n**Usage**: `{command.usage}`",
                              color=0x800080)
        embed.set_thumbnail(url=ctx.author.avatar.url)
        
        return await ctx.reply(embed=embed)
    
async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))