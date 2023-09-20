import discord 
from discord.ext import commands 
from discord import Intents 
import config

cogs = ['social', 'help']

class Delta(commands.Bot): 
    
    def __init__(
        self,
        *args,
        **kwargs
    ):
        
        
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
        print(f"Online on user {self.user.name}\n{round(self.latency*100)} ms")
    
    


if __name__ == '__main__':
    Delta()
    
    
    