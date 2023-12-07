from typing import Any, Optional
import discord
from discord.interactions import Interaction


class AutoModSelectMenu(discord.ui.Select):
    
    def __init__(self):
        options = [
            discord.SelectOption(label='Auto Delete', emoji='💀', description='Informações sobre este módulo.'),
            discord.SelectOption(label='Auto Ban', emoji='💀', description='Informações sobre este módulo.'),
            discord.SelectOption(label='Auto Purge', emoji='💀', description='Informações sobre este módulo.'),
            discord.SelectOption(label='Auto Kick', emoji='💀', description='Informações sobre este módulo.')
        ]
        super().__init__(placeholder='Selecione uma opção', custom_id='automod_select_menu', max_values=1, min_values=1, options=options)
        
    async def callback(self, interaction: Interaction):
        pass 


class AutomodView(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(AutoModSelectMenu())