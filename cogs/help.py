from discord.ext import commands 
import discord 
from helpers import utils
from json import load

class HelpCog(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
        self.hidden_cogs = ['CommandsErrors', 'HelpCog', 'Mongo',
                            'Reminder', 'Purge']
        self.emotes = utils.Emotes()
        
        with open("src/assets/links.json", "r") as f:
            self.links = load(f)

    
    @commands.command(
        name='help',
        description='Veja todos os meus comandos disponíveis.',
        hidden=True
    )
    async def ajuda(self, ctx: commands.Context, *, command_name: str = None):
        
        
        if command_name is None:
            
            embed = discord.Embed(title="Meus Comandos", description=f"Use `{self.bot.command_prefix}help <command_name>` para obter informações adicionais sobre tal comando.",color=0x800080)
            
            cogs = [x for x in self.bot.cogs if x not in self.hidden_cogs]
            
            for cog in cogs:
                
                text = ""
                
                commands_=[]
                
                for f in self.bot.get_cog(cog).get_commands():
                    
                    if isinstance(f, commands.Group):

                        subcmd = ""

                        for subcommand in f.walk_commands():

                            if subcommand.parents[0] == f:
                                commands_.append(subcommand)
                            else:
                                continue
                    
                    commands_.append(f)

                for x in commands_:
                    text += f"`{self.bot.command_prefix}{x.name}` "
                
                

                embed.add_field(name=self.bot.get_cog(cog).qualified_name, value=text, inline=True)
            
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_image(url=self.links['help_image'])
            return await ctx.reply(embed=embed)

        command = self.bot.get_command(command_name) 
        
        if command is None:
            return await ctx.send(f"`{command_name}` não é um comando válido.")

        aliases = ''
        
        if len(command.aliases) > 0:
            
            for i in command.aliases:
                aliases += f"`{i}` "
        else:
            aliases = f'Não tem. {self.emotes.nhe}'
            
            
        embed = discord.Embed(title=command.name,
                              color=0x800080)
       
        embed.set_thumbnail(url=ctx.author.avatar.url)
        embed.add_field(
            name=f"{self.emotes.audit} Descrição do comando",
            value=f"`{command.description or f'Não foi inserido. {self.emotes.nhe}'}`"
        )
        embed.add_field(
            name=f"{self.emotes.info} Como usar",
            value=f"`{command.usage or f'Não inserido. {self.emotes.nhe}'}`"
        )
        embed.add_field(
            name="Aliases do comando",
            value=aliases
        )
        embed.set_image(url=self.links['help_image'])
        return await ctx.reply(embed=embed)
    
async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))