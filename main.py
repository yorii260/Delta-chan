import discord 
from discord.ext import commands 
from discord import Intents 
import config

cogs = ['social', 'help',
        'moderation', 'commandsError',
        'mongo']

class Delta(commands.Bot): 
    
    def __init__(
        self,
        *args,
        **kwargs
    ):
        
        self.maintenance = False 
        
        super().__init__(
            *args,
            **kwargs,
            command_prefix='d.',
            help_command=None, 
            strip_after_prefix=True,
            intents=Intents.all()
        )
        
        self.run(config.token)
    
    
    async def setup_hook(self) -> None:
        
        if len(cogs) > 0:
            
            for cog in cogs:
                await self.load_extension(f'cogs.{cog}')
                print(f"Sucessfully loaded cogs.{cog} extension.")
                
            print("="*30)
        
    
    
    async def on_ready(self) -> None:
        print(f"Online on user {self.user.name}\n{round(self.latency*100)} ms.")
        await self.delta_activity()
    
    async def delta_activity(self):
        activity = discord.Streaming(name='d.help', url='https://twitch.tv/glz007', game='Discord')
        await self.change_presence(status=discord.Status.online if not self.maintenance else discord.Status.dnd, activity=activity)
    
    
    @property
    def mongo(self):
        return self.get_cog("Mongo")
    

    
    
if __name__ == '__main__':
    Delta()
    
    
    