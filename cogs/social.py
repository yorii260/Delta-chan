from discord.ext import commands
import discord 
from helpers import utils, converters
from src.views.SocialViews import UiView
import random
from datetime import datetime, timedelta
import re
from dateutil import tz 


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
                        value=f"<t:{int(user.joined_at.timestamp())}:R>"
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
                      aliases=("rm",),
                      usage='d.remind <time> <remind>')
    async def remind(self, ctx: commands.Context, reminder: converters.DateConverter, *, reason: str):
        
        '''x = [x for x in re.sub(r"[0-9]", '.', time).strip().split('.') if x != '']
        y = [x for x in re.sub("[a-zA-Z]", '.', time).strip().split('.') if x != '']
        
        inc = 0 
        
        for r in x:
            
            if r in ['min', 'm', 'minutes', 'minutos']:
                inc += int(y[x.index(r)])*60
            elif r in ['s', 'seconds', 'segundos']:
                inc += int(y[x.index(r)])
            elif r in ['h', 'hours', 'horas']:
                inc += int(y[x.index(r)])*3600'''
            
        
        increment = datetime.now() + reminder
        embed = discord.Embed(title="Lembrete registrado!", description=f"Pode ficar tranquilo(a) que eu irei te avisar!\nTe vejo em <t:{int(increment.timestamp())}:R>",
                              color=0x800080)
        embed.set_thumbnail(url=ctx.author.avatar.url)
        
        await ctx.reply(embed=embed)
        
         
        return self.bot.mongo.reminders.insert_one(
            {"reminder": 
                {
                    "user_id": ctx.author.id,
                    "channel_id": ctx.channel.id,
                    "remind": reason,
                    "in": increment,
                    "last_check": datetime.now()
                }
            }
        )
    
    
    @commands.command(name='invite',
                      description='Me adicione em outro servidor <3.')
    async def invite(self, ctx: commands.Context):
        
        embed = discord.Embed(title="Me adicione em outro servidor!",
                              description=f"Clique [aqui](https://discord.com/api/oauth2/authorize?client_id=1178489335826354206&permissions=8&scope=bot) para me adicionar à outro servidor.")
        embed.color = 0x800080
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)
    
    
    @commands.command(name='afk',
                      description='Se ausente e sempre deixe uma mensagem para quem lhe marcar.',
                      usage="d.afk <motivo>")
    async def afk(self, ctx: commands.Context, *, args: str):
        
        insert = {
            "user_id": ctx.author.id,
            "guild_id": ctx.guild.id,
            "reason": args, 
            "afk_date": [f"<t:{utils.now_time()}:R>", datetime.now(tz=tz.gettz('America/Sao_Paulo')).strftime("%d/%m/%y às %H:%M")]
        }
        
        self.bot.mongo.afk.insert_one(insert)
        return await ctx.send(f"{ctx.author.mention}, AFK ativado. Para remover-lo, basta enviar uma mensagem em qualquer chat que eu tenha permissão de ver.")
    
    
async def setup(bot: commands.Bot):
    await bot.add_cog(SocialCommands(bot))