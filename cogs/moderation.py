from discord.ext import commands 
import discord
from src.views.moderation_views import BanView, ConfirmEditWarn
import typing

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
    @commands.cooldown(1, 10, commands.BucketType.user)
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
        return await self.bot.mongo.insert_warn(user, ctx.guild.id, ctx.author, reason)
    
    
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    @commands.command(
        name='list_warns',
        description="Veja os warns que algum usuário de seu servidor tem.",
        usage="d.list_warns <user>",
        aliases=("lw",)
    )
    async def list_warns(self, ctx: commands.Context, user: discord.Member | discord.User):
        
        user_ = self.bot.mongo.list_warns(user)
        
        em = discord.Embed(title=f"{user.name} Warns", description=user_ if user_ is not None else "Nada.", color=0x800080)
        em.set_thumbnail(url=user.avatar.url)
        return await ctx.send(embed=em)
        
    
    """@commands.Cog.listener()
    async def on_warn_submit(self, warned_user: discord.Member, moderator_user: discord.Member, reason: str):
        
        channel = self.bot.mongo.audit_channel()

        if channel is None:
            return 
        
        channel = self.bot.get_channel(int(channel))
        
        em = discord.Embed(title=f"{warned_user.name} recebu um aviso.", description=f"**Moderador**: {moderator_user.mention}\n**Motivo**: `{reason}`",
                           color=0x800080)
        em.set_thumbnail(url=warned_user.avatar.url)
        
        return await channel.send(embed=em)"""
    
        
    @commands.has_guild_permissions(administrator=True)
    @commands.command(name='set_audit_channel',
                      description="Adicione um canal para os logs do bot.",
                      usage="d.sac <channel>",
                      aliases=("sac",))
    async def set_audit(self, ctx: commands.Context, channel: discord.TextChannel):
        current = self.bot.mongo.audit_channel()
        
        if channel.id == current:
            return await ctx.reply(f"{channel.mention} já é o atual canal de log, tente com outro")
        
        r = self.bot.mongo.update_audit_channel(channel)
        
        if r is not None:
            return await ctx.reply(f"{channel.mention} foi setado como canal de logs.")
        else:
            print("Alguma coisa de errado ocorreu.")
            
    
    
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    @commands.command(name='delete_warn',
                      description="Remova um warn de algum membro pelo seu id.",
                      usage='d.rw <warn id>',
                      aliases=("rw",))
    async def remove_warn(self, ctx: commands.Context, warn_id: str):
        
        r = self.bot.mongo.delete_warn(warn_id)
        
        if r is not None:
            return await ctx.reply(f"O warn `{warn_id}` foi removido com sucesso.")
    
    
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    @commands.command(
        name='edit_warn',
        description="Edite o motivo de um warn usando o ID",
        usage="d.ew <warn id> <new reason>",
        aliases=("ew",)
    )
    async def edit_warn(self, ctx: commands.Context, warn_id: str, *, new_reason: str):
        
        w = self.bot.mongo.warns.find_one({"warn_id": warn_id})
        
        if w is None:
            return await ctx.reply(f"`{warn_id}` é um id inválido, você digitou corretamente ou esse warn existe?")

        embed = discord.Embed(title="Confirme a edição",
                              description=f"Ao confirmar a reason da warn do usuário <@{w['id_']}> passará de `{w['motivo']}` para `{new_reason}`\nVocê confirma esta ação?",
                              color=0x800080)

        await ctx.send(embed=embed, view=ConfirmEditWarn(ctx))
        
        return self.bot.mongo.warns.update_one({"warn_id": warn_id}, {"$set": {"motivo": new_reason}})

    
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.command(
        name='massban',
        description='Bane vários usuários utilizando o id.',
        usage='d.massban user1, user2',
        aliases=('mb',)
    )
    async def massban(self, ctx: commands.Context, *args: int | str | discord.User):
        
        users = []
        reason = ''
        
        for i in args:
            
            if type(i) in (int, discord.User):
                users.append(i if type(i) == int else i.id) 
            
            else:
                reason += f'{i} '
        
        
        for user in users:
            
            try:
                user = self.bot.get_user(user)
                
                await ctx.guild.ban(user, reason=reason)
            except Exception as e:
                self.bot.log.warning(e)
        
        return await ctx.reply(f"Um total de `{len(users)}` usuários foram banidos com sucesso.")
    

    @commands.is_owner()
    @commands.command(name="show_automod",
                      usage="d.show_automod config",
                      hidden=True,
                      aliases=("sd",))
    async def sw(self, ctx: commands.Context, config: str = None):

        if config is None:
            return await ctx.reply("Argumento inválido.")
        
        data = [x for x in self.bot.mongo.automod.find()][0]['automod_config'][config]

        return await ctx.send(f"```json\n{data}\n```", ephemeral=True)
    
async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))