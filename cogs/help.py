from discord.ext import commands 
import discord 
from helpers import utils
from json import load

class HelpCog(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
        self.hidden_cogs = ['CommandsErrors', 'HelpCog', 'Mongo',
                            'Reminder', 'Purge',
                            'GeralEventListener',
                            'RunningTasks']
        self.emotes = utils.Emotes()
        
        with open("src/assets/links.json", "r") as f:
            self.links = load(f)

    
    @commands.command(
        name='help',
        description='Veja todos os meus comandos disponíveis.',
        hidden=True
    )
    async def ajuda(self, ctx: commands.Context, *, command_name: str = None):

        embed = discord.Embed(color=0x800080)


        if command_name is None:

            cogs = [x for x in self.bot.cogs.values() if x.qualified_name not in self.hidden_cogs]

            for cog in cogs:

                commands = [x for x in cog.get_commands() and cog.walk_commands()]
                text = ""

                for command in commands:
                    
                    if not command.hidden:
                        text += f"`{command}`\n"

                
                embed.add_field(
                    name=cog.qualified_name,
                    value=text,
                    inline=True
                )
                
            embed.title = "Meus Comandos <3"
            embed.description = f"Use `{self.bot.command_prefix}help <command>` para obter informações adicionais sobre tal comando."
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_image(url=self.links.get("help_image"))

            return await ctx.reply(embed=embed)

        else:

            command = self.bot.get_command(command_name.lower())
            aliases = "";

            for x in command.aliases:
                aliases += f"`{x.strip()}`\n"

            embed.title = f"{command.cog_name}: {command.name}"
            embed.add_field(
                name=f"{self.emotes.audit} Descrição do comando",
                value=f"`{command.description}`",
                inline=True
            )  
            embed.add_field(
                name=f"{self.emotes.info} Como usar",
                value=f"`{command.usage}`",
                inline=True 
            )
            embed.add_field(
                name=f"Aliases do comando",
                value=aliases, 
                inline=True
            )

            embed.set_thumbnail(url=self.bot.user.avatar.url)
            return await ctx.reply(embed=embed)
    
async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))