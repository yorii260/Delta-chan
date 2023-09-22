from typing import Any, Coroutine
import discord 

class BanView(discord.ui.View):
    
    def __init__(self, data, timeout=60):
        self.data = data 
        super().__init__(timeout=timeout)
    
    
    @discord.ui.button(
        label='Confirmar',
        custom_id='confirm_ban',
        style=discord.ButtonStyle.green
    )
    async def ban_confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        user, ctx, reason = self.data 
        
        em = discord.Embed(title='Ban realizado com sucesso',
                           color=0x800080,
                           description=f"O usuário `{user.name}` foi banido com sucesso!\nMotivo: `{reason}`")
        
        await interaction.response.edit_message(embed=em, view=None)
        return await user.ban(reason=reason)
    
    
    @discord.ui.button(
        label='Cancelar',
        custom_id='cancelar_button',
        style=discord.ButtonStyle.red
    )
    async def cancelar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        em = discord.Embed(color=0xff0000, description='Banimento cancelado')
        return await interaction.response.edit_message(embed=em, view=None)


    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.data[1].author.id:
            return False 
        else:
            return True


class ConfirmEditWarn(discord.ui.View):
    
    def __init__(self, ctx, timeout=30):
        self.ctx = ctx 
        super().__init__(timeout=timeout)
    
    
    @discord.ui.button(label="Confirmar",
                       style=discord.ButtonStyle.green,
                       custom_id="confirm_edit_warn_buttton")
    async def c_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        em = discord.Embed(title='Edição feita com sucesso!', color=0x00FF00)
        em.set_thumbnail(url=self.ctx.author.avatar.url)
        
        return await interaction.response.edit_message(embed=em, view=None)

    
    @discord.ui.button(label="Cancelar",
                       style=discord.ButtonStyle.red,
                       custom_id="cancel_edit_warn_buttton")
    async def cc_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        em = discord.Embed(title='Edição cancelada com sucesso!', color=0xff0000)
        em.set_thumbnail(url=self.ctx.author.avatar.url)
        
        return await interaction.response.edit_message(embed=em, view=None)
    
    
    async def interaction_check(self, interaction: discord.Interaction):
        
        if interaction.user != self.ctx.author:
            return False 
        else:
            return True

        