import discord
from discord.ext import commands
from pymongo.collection import Collection
from helpers.utils import random_id, Emotes
from datetime import datetime, timedelta


class AutoModSelectMenu(discord.ui.Select):
    
    def __init__(self, bot: commands.Bot):

        self.emotes = Emotes()

        options = [
            discord.SelectOption(label='Auto Delete', emoji=self.emotes.delete, description='Veja e gerencie o módulo Auto Delete.'),
            discord.SelectOption(label='Auto Ban', emoji=self.emotes.banned, description='Veja e gerencie o módulo Auto Ban.'),
            discord.SelectOption(label='Auto Purge', emoji=self.emotes.purge, description='Veja e gerencie o módulo Auto Purge'),
            discord.SelectOption(label='Auto Kick', emoji=self.emotes.kick, description='Veja e gerencie o módulo Auto Kick')
        ]
        self.bot = bot
        super().__init__(placeholder='Selecione uma opção', custom_id='automod_select_menu', max_values=1, min_values=1, options=options)
        
    async def callback(self, interaction: discord.Interaction):
        
        embed = discord.Embed(color=0x800080)
        database: Collection = self.bot.mongo.automod
        
        
        if self.values[0] == 'Auto Delete':
            
            x: dict = [f for f in database.find()][0]['automod_config']['auto_delete_config']
            embed.title = 'Auto Delete'
            
            embed.add_field(
                name='Estado',
                value="✅" if x['auto_delete_id'] != '' else '❌',
                inline=False
            )
            embed.add_field(
                name='Active channel',
                value=f"<#{x['auto_delete_channel_id']}>" if x['auto_delete_id'] != '' else "None",
                inline=False
            )

            if x['auto_delete_filter'] not in ["", "default"]:
                embed.add_field(
                    name='Filtro',
                    value=f"{'Ends with' if self.bot.auto_delete.type == 'EW' else 'Starts with'} `{self.bot.auto_delete.filter}`",
                    inline=False
                )
            else:
                pass 

            return await interaction.response.send_message(embed=embed, ephemeral=True, view=AutoDeleteButtons(self.bot))
            
        elif self.values[0] == 'Auto Ban':
            
            embed.title = 'Auto Ban'
            y: dict = [f for f in database.find()][0]['automod_config']['auto_ban_config']
                
            embed.add_field(
                name='Active',
                value='✅' if y['auto_ban_id'] != '' else '❌',
                inline=False 
            )
            embed.add_field(
                name='Filter',
                value=y['auto_ban_when'] or "Não definido."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        elif self.values[0] == 'Auto Purge':
            
            embed.title = 'Auto Purge'
            z: dict = [f for f in database.find()][0]['automod_config']['auto_purge_config']
            date = lambda date: datetime.fromisoformat(str(date))
            
            embed.add_field(
                name='Active',
                value='✅' if z['auto_purge_id'] != '' else '❌',
                inline=False
            )
            embed.add_field(
                name='Purge channel',
                value=f"<#{z['auto_purge_channel_id']}>" if z['auto_purge_id'] != '' else 'Não definido.',
                inline=False
            )
            embed.add_field(
                name='Next purge',
                value=f"<t:{int(date(z['next_purge']).timestamp())}:R>" if z['auto_purge_id'] != '' else "Não definido.",
                inline=False
            )

            if z['auto_purge_id'] != '':
                embed.add_field(
                    name="Last check",
                    value=f"<t:{int(date(z['last_check']).timestamp())}:R>",
                    inline=False
                )
            return await interaction.response.send_message(embed=embed, view=AutoPurgeButtons(self.bot))
        
        elif self.values[0] == 'Auto Kick':
            
            embed.title = 'Auto Kick'
            xy: dict = [f for f in database.find()][0]['automod_config']['kick_new_account_config']
            
            embed.add_field(
                name='Active',
                value='✅' if xy['auto_kick_id'] != '' else '❌',
                inline=False 
            )
            embed.add_field(
                name='Min time to kick new users',
                value=xy['auto_kick_minimum_time'] if xy['auto_kick_id'] != '' else 'Não definido.'
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
            

class AutomodView(discord.ui.View):
    def __init__(self, bot, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(AutoModSelectMenu(bot))
       
    
class AutoPurgeModal(discord.ui.Modal):

    def __init__(self, bot: commands.Bot):
        super().__init__(title="Auto Purge", timeout=60, custom_id="auto_purge_modal")

        self.purge_delay = discord.ui.TextInput(label="Delay do purge",
                                                placeholder="Digite o tempo em segundos.",
                                                min_length=1,
                                                max_length=4,
                                                style=discord.TextStyle.short,
                                                custom_id="purge_delay_label")
        
        self.purge_channel = discord.ui.TextInput(
            label="ID do canal",
            custom_id='auto_purge_channel',
            placeholder='Digite ou cole o id do canal.',
            max_length=20,
            min_length=1
        )

        self.bot = bot 
        self.add_item(self.purge_channel)
        self.add_item(self.purge_delay)

    
    async def on_submit(self, interaction: discord.Interaction):

        update = {
            "auto_purge_channel_id": int(self.purge_channel.value),
            "auto_purge_delay": int(self.purge_delay.value),
            "auto_purge_id": random_id(),
            "auto_purge_guild_id": self.bot.get_channel(int(self.purge_channel.value)).guild.id
        }

        x: dict = [f for f in self.bot.mongo.automod.find()][0]

        x['automod_config']['auto_purge_config'].update(update)

        if self.purge_channel != "":
            await interaction.response.send_message(f"{interaction.user.mention}, obrigado!", ephemeral=True)
            return self.bot.mongo.automod.update_one({"_id": x['_id']}, {"$set":{"automod_config":x['automod_config']}})
    

class AutoPurgeButtons(discord.ui.View):

    def __init__(self, bot: commands.Bot, *, timeout=50):
        super().__init__(timeout=timeout)

        self.bot = bot


    @commands.has_permissions(administrator=True)
    @discord.ui.button(
        label="Desativar",
        custom_id="purge_desactive",
        style=discord.ButtonStyle.red
    )
    async def des_button(self, interaction: discord.Interaction, button: discord.Button):
        x: dict = [f for f in self.bot.mongo.automod.find()][0]

        update = {
            "auto_purge_id": "",
            "auto_purge_channel_id": "",
            "auto_purge_guild_id":  "",
            "last_check": "",
            "next_purge": ""
        }

        if x['automod_config']['auto_purge_config'].get("auto_purge_id") == "":
            return await interaction.response.send_message("Atualmente o módulo está desativado.")
        
        x['automod_config']['auto_purge_config'].update(update)
        self.bot.mongo.automod.update_one({"_id": x['_id']}, {"$set":{"automod_config":x['automod_config']}})
        
        self.bot.get_cog("Purge").update_purge_time.cancel()
        return await interaction.response.send_message("O módulo Auto Purge foi desativado.")
    

    @commands.has_permissions(administrator=True)
    @discord.ui.button(
        label="Ativar",
        custom_id="ativar_purge",
        style=discord.ButtonStyle.green
    )
    async def act_button(self, interaction: discord.Interaction, button: discord.Button):

        x = [x for x in self.bot.mongo.automod.find()][0]

        class ChannelModal(discord.ui.Modal):

            def __init__(self, bot: commands.Bot):
                super().__init__(title="Auto Purge - Channel ID", timeout=50, custom_id="channel_purge")

                self.channel = discord.ui.TextInput(label="ID do canal", placeholder="Digite aqui", required=True, min_length=1, max_length=50)
                self.bot = bot 

                self.add_item(self.channel)

            async def on_submit(self, interaction: discord.Interaction):

                update = {
                    "auto_purge_channel_id": self.channel.value
                }

                x = [x for x in self.bot.mongo.automod.find()][0]

                x['automod_config']['auto_purge_config'].update(update)
                self.bot.mongo.automod.update_one({"_id": x['_id']}, {"$set":{"automod_config":x['automod_config']}})

                return await interaction.response.send_message("O módulo foi ativado com sucesso!", ephemeral=True)

        update = {
            "auto_purge_id": random_id(),
            "next_purge": datetime.now() + timedelta(seconds=3600),
            "last_check": datetime.now(),
            "auto_purge_guild_id": interaction.guild_id
        }

        if x['automod_config']['auto_purge_config'].get("auto_purge_id") != "":
            return await interaction.response.send_message("O módulo já está ativado.")

        x['automod_config']['auto_purge_config'].update(update)

        self.bot.mongo.automod.update_one({"_id": x['_id']}, {"$set":{"automod_config":x['automod_config']}})
        self.bot.get_cog("Purge").update_purge_time.start()

        return await interaction.response.send_modal(ChannelModal(self.bot))

    
    
class AutoDeleteButtons(discord.ui.View):

    def __init__(self, bot: commands.Bot, *, timeout=50):
        super().__init__(timeout=timeout)

        self.bot = bot


    @commands.has_permissions(administrator=True)
    @discord.ui.button(
        label="Desativar",
        custom_id="delete_desactive",
        style=discord.ButtonStyle.red
    )
    async def des_button(self, interaction: discord.Interaction, button: discord.Button):
        x: dict = [f for f in self.bot.mongo.automod.find()][0]

        update = {
            "auto_delete_id": "",
            "auto_delete_channel_id": "",
            "auto_delete_filter":  "",
            "auto_delete_type": ""
        }

        if x['automod_config']['auto_delete_config'].get("auto_delete_id") == "":
            return await interaction.response.send_message("Atualmente o módulo está desativado.")
        
        x['automod_config']['auto_delete_config'].update(update)
        self.bot.mongo.automod.update_one({"_id": x['_id']}, {"$set":{"automod_config":x['automod_config']}})
        
        return await interaction.response.send_message("O módulo Auto Delete foi desativado.")
    

    @commands.has_permissions(administrator=True)
    @discord.ui.button(
        label="Ativar",
        custom_id="ativar_delete",
        style=discord.ButtonStyle.green
    )
    async def act_button(self, interaction: discord.Interaction, button: discord.Button):

        x = [x for x in self.bot.mongo.automod.find()][0]


        update = {
            "auto_delete_id": random_id()
        }

        if x['automod_config']['auto_delete_config'].get("auto_delete_id") != "":
            return await interaction.response.send_message("O módulo já está ativado.")

        x['automod_config']['auto_delete_config'].update(update)
        
        class ChannelModal(discord.ui.Modal):

            def __init__(self, bot: commands.Bot):
                super().__init__(title="Auto Delete - Channel/Filter", timeout=50, custom_id="channel_delete")

                self.channel = discord.ui.TextInput(label="ID do canal", placeholder="Digite aqui", required=True, min_length=1, max_length=50)
                self.filter = discord.ui.TextInput(label="Filter", placeholder="Digite a mensagem de referencia para apagar.", min_length=3, max_length=50)
                self.type = discord.ui.TextInput(label="Type of filter", placeholder="EW: Ends With | SW: Starts With", min_length=2, max_length=2)
                self.bot = bot 

                self.add_item(self.channel)
                self.add_item(self.filter)
                self.add_item(self.type)

            async def on_submit(self, interaction: discord.Interaction):

                update = {
                    "auto_delete_channel_id": self.channel.value,
                    "auto_delete_filter": self.filter.value,
                    "auto_delete_type": self.type.value
                }

                x = [x for x in self.bot.mongo.automod.find()][0]

                x['automod_config']['auto_delete_config'].update(update)
                self.bot.mongo.automod.update_one({"_id": x['_id']}, {"$set":{"automod_config":x['automod_config']}})

                return await interaction.response.send_message("O módulo foi ativado com sucesso!", ephemeral=True)
        

        await interaction.response.send_modal(ChannelModal(self.bot))
        
        return self.bot.mongo.automod.update_one({"_id": x['_id']}, {"$set":{"automod_config":x['automod_config']}})
        

        