import discord
from discord.ext import commands
from pymongo.collection import Collection
from discord import Button, ButtonStyle
from helpers.utils import random_id


class AutoModSelectMenu(discord.ui.Select):
    
    def __init__(self, bot: commands.Bot):
        options = [
            discord.SelectOption(label='Auto Delete', emoji='💀', description='Informações sobre este módulo.'),
            discord.SelectOption(label='Auto Ban', emoji='💀', description='Informações sobre este módulo.'),
            discord.SelectOption(label='Auto Purge', emoji='💀', description='Informações sobre este módulo.'),
            discord.SelectOption(label='Auto Kick', emoji='💀', description='Informações sobre este módulo.')
        ]
        self.bot = bot
        super().__init__(placeholder='Selecione uma opção', custom_id='automod_select_menu', max_values=1, min_values=1, options=options)
        
    async def callback(self, interaction: discord.Interaction):
        
        embed = discord.Embed(color=0x800080)
        database: Collection = self.bot.mongo.automod
        
        
        if self.values[0] == 'Auto Delete':
            
            x: dict = [f for f in database.find()][0]['automod_config']['auto_delete_config']
            embed.title = 'Auto Delete'
            
            if x['auto_delete_id'] != '':
                
                embed.add_field(
                    name='Active',
                    value='Sim',
                    inline=False
                )
                embed.add_field(
                    name='Active channel',
                    value=f"<#{x['auto_delete_channel_id']}>",
                    inline=False
                )
                embed.add_field(
                    name='Filter',
                    value=f"{'Starts with ' if x['auto_delete_filter'].split(':')[0] == 'SW' else 'Ends with '}{x['auto_delete_filter'].split(':')[1].capitalize()}",
                    inline=False
                )
            
        elif self.values[0] == 'Auto Ban':
            
            embed.title = 'Auto Ban'
            y: dict = [f for f in database.find()][0]['automod_config']['auto_ban_config']
                
            embed.add_field(
                name='Active',
                value='Sim' if y['auto_ban_id'] != '' else 'Não',
                inline=False 
            )
            embed.add_field(
                name='Filter',
                value=y['auto_ban_when'] or "Não definido."
            )
        
        elif self.values[0] == 'Auto Purge':
            
            embed.title = 'Auto Purge'
            z: dict = [f for f in database.find()][0]['automod_config']['auto_purge_config']
            
            embed.add_field(
                name='Active',
                value='Sim' if z['auto_purge_id'] != '' else 'Não',
                inline=False
            )
            embed.add_field(
                name='Purge channel',
                value=f"<#{z['auto_purge_channel_id']}>" if z['auto_purge_id'] != '' else 'Não definido.',
                inline=False
            )
            embed.add_field(
                name='Purge delay',
                value=f"{z['auto_purge_delay']} seconds" if z['auto_purge_id'] != '' else "Não definido.",
                inline=False
            )
        
        elif self.values[0] == 'Auto Kick':
            
            embed.title = 'Auto Kick'
            xy: dict = [f for f in database.find()][0]['automod_config']['kick_new_account_config']
            
            embed.add_field(
                name='Active',
                value='Sim' if xy['kick_id'] != '' else 'Não',
                inline=False 
            )
            embed.add_field(
                name='Min time to kick new users',
                value=xy['kick_minimum_time'] if xy['kick_id'] != '' else 'Não definido.'
            )
            
        return await interaction.response.send_message(embed=embed, ephemeral=True)


class AutomodView(discord.ui.View):
    def __init__(self, bot, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(AutoModSelectMenu(bot))
    

class AutomodConfigView(discord.ui.View):
    
    def __init__(self, bot: commands.Bot, *, timeout=60):
        super().__init__(timeout=timeout)
        
        self.bot = bot 
    
    @discord.ui.button(
        label='Auto Delete',
        custom_id='auto_delete_button',
        style=ButtonStyle.blurple
    )
    async def button_auto_del(self, interaction: discord.Interaction, button: Button):
        return await interaction.response.send_modal(AutoDeleteModal(self.bot))
    
    @discord.ui.button(
        label='Auto Ban',
        custom_id='auto_ban_button',
        style=ButtonStyle.blurple
    )
    async def button_auto_ban(self, interaction: discord.Interaction, button: Button):
        pass
    
    @discord.ui.button(
        label='Auto Kick',
        custom_id='auto_kick_button',
        style=ButtonStyle.blurple
    )
    async def button_auto_kick(self, interaction: discord.Interaction, button: Button):
        pass
    
    @discord.ui.button(
        label='Auto Purge',
        custom_id='auto_purge_button',
        style=ButtonStyle.blurple
    )
    async def button_auto_purge(self, interaction: discord.Interaction, button: Button):
        pass
    

class AutoDeleteModal(discord.ui.Modal):
    
    def __init__(self, bot: commands.Bot):
        super().__init__(title='Auto Delete', timeout=60, custom_id='auto_delete_modal')
        
        self.filter = discord.ui.TextInput(label='Filter', 
                                           placeholder='Digite a palavra-chave.', 
                                           min_length=2, 
                                           max_length=50, 
                                           style=discord.TextStyle.short,
                                           custom_id='filter_text')

        self.channel = discord.ui.TextInput(
            label="ID do canal",
            custom_id='auto_del_channel',
            placeholder='Digite ou cole o id do canal.',
            max_length=19,
            min_length=19
        )
        
        self.bot = bot
        self.add_item(self.filter)
        self.add_item(self.channel)
        
    async def on_submit(self, interaction: discord.Interaction):
        
        update = {
            "auto_delete_channel_id": int(self.channel.value),
            "auto_delete_filter": f"SW:{self.filter.value}",
            "auto_delete_punish": "",
            "auto_delete_id": random_id()
        }
        x: dict = [f for f in self.bot.mongo.automod.find()][0]
        x['automod_config']['auto_delete_config'].update(update)
        if self.filter.value != '':
            await interaction.response.send_message(f"{interaction.user.mention}, obrigado!", ephemeral=True)
            return self.bot.mongo.automod.update_one({"_id": x['_id']}, {"$set":{"automod_config":x['automod_config']}})
    
    
            
            
    