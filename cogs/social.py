from discord.ext import commands
import discord 
from helpers import utils
from src.views.SocialViews import UiView
import random
from datetime import datetime, timedelta


class SocialCommands(commands.Cog, name="Social"):
    
    """
    Todos os comandos relacionados à uso geral estará presente aqui.
    
    """
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
        self.emotes = utils.Emotes()
        
    
    
    #@commands.cooldown(1, 10, type=commands.BucketType.user)
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

    
    @commands.guild_only()
    @commands.command(name='roll',
                      description='Gire o dado e consiga um valor aléatório.',
                      usage='d.roll <qty>')
    async def roll(self, ctx: commands.Context, qty: int = 10):
        return await ctx.send(f"Eu girei o 🎲 e obtive o número: `{random.randint(1, qty)}`")
    
    
    @commands.guild_only()
    @commands.is_owner()
    @commands.command(hidden=True, name='status')
    async def status(self, ctx: commands.Context):
        
        cogs = len(self.bot.cogs)
        commands = len(self.bot.commands)
        
        desc = f"- Feito em Python. {self.emotes.python}\n- `{cogs}` extensões foram carregadas.\n- `{commands}` comandos disponíveis.\n- Meu ping atual é de `{round(self.bot.latency*100)}` ms."
        
        em = discord.Embed(title=f'{self.bot.user.name} Stats', description=desc, color=0x800080)
        em.set_thumbnail(url=self.bot.user.avatar.url)
        
        return await ctx.reply(embed=em, ephemeral=True)
    
        
    @commands.guild_only()
    @commands.command(name='remind',
                      description='Adicione um lembrete e eu irei te lembrar!',
                      aliases=("rm",))
    async def remind(self, ctx: commands.Context, time: int, *, reminder: str):
        
        increment = datetime.now() + timedelta(minutes=time)
        embed = discord.Embed(title="Lembrete registrado!", description=f"Pode ficar tranquilo(a) que eu irei te avisar!\nTe vejo em <t:{int(increment.now().timestamp())}:f>",
                              color=0x800080)
        embed.set_thumbnail(url=ctx.author.avatar.url)
        
        await ctx.reply(embed=embed)
        
         
        return self.bot.mongo.reminders.insert_one(
            {"reminder": 
                {
                    "user_id": ctx.author.id,
                    "channel_id": ctx.channel.id,
                    "remind": reminder,
                    "in": increment,
                    "last_check": datetime.now()
                }
            }
            )
    
                
        
async def setup(bot: commands.Bot):
    await bot.add_cog(SocialCommands(bot))