import discord 


class UiView(discord.ui.View):
    
    def __init__(self, user: discord.User, timeout=180):
        self.user = user 
        super().__init__(timeout=timeout)
            
    @discord.ui.button(label='Avatar', custom_id='avatar_button', style=discord.ButtonStyle.green)
    async def button_avatar(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        em = discord.Embed(color=0x800080)
        em.set_image(url=self.user.avatar.url)
        
        return await interaction.response.send_message(embed=em, ephemeral=True)

    
    async def on_timeout(self):
        return self.stop()
    
    