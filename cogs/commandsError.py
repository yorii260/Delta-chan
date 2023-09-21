import discord 
from discord.ext import commands 


class CommandsErrors(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
    
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"O parâmetro `{error.param.name}` é obrigatório e o mesmo não foi inserido.")
        
        elif isinstance(error, commands.MissingPermissions):
            
            perms = ''
            for role in error.missing_permissions:
                perms += f"`{role.replace('_', ' ').capitalize()}`"
            
            return await ctx.reply(f'Você precisa {f"das permissões para usar este comando: {perms}" if len(error.missing_permissions) > 1 else f"da permissão {perms} para usar este comando."}')

        elif isinstance(error, commands.NoPrivateMessage):
            return await ctx.send('Você não pode usar este comando das mensagens privadas.')

        
        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f"Espere `{int(error.retry_after)} segundo{'s' if error.retry_after > 1 else ''}` para usar este comando novamente.")

        
        elif isinstance(error, commands.BotMissingPermissions):
            perm = ''
            
            for role in error.missing_permissions:
                perm += f"`{role.replace('_','').capitalize()}`"
            
            return await ctx.reply(f'Você precisa {f"das permissões para usar este comando: {perm}" if len(error.missing_permissions) > 1 else f"da permissão {perm} para usar este comando."}')
            

async def setup(bot: commands.Bot):
    await bot.add_cog(CommandsErrors(bot))