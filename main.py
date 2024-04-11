import discord 
from discord.ext import commands 
from discord import Intents 
import config
import logging, sys 
from colorama import Fore
from pymongo.collection import Collection
import cogs as c

cogs = ['social', 'help',
        'moderation', 'commandsError',
        'mongo', "automod"]

events = [
    "listeners",
    "tasks_running"
]


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
            command_prefix="d.",
            help_command=None, 
            strip_after_prefix=True,
            intents=Intents.all()
        )
        
        self.setup_logging()
        self.run(config.token, root_logger=self.log, log_handler=None)
    
    
    async def setup_hook(self) -> None:
        
        if len(cogs) > 0:
            
            for cog in cogs:
                await self.load_extension(f'cogs.{cog}')
                self.log.info(f"Sucessfully loaded cogs.{cog} extension.")

        if len(events) > 0:

            for event in events:
                await self.load_extension(f"events.{event}")
                self.log.info("Sucessfully loaded events.%s extension.", event)

            print("="*30)
        
    
    
    async def on_ready(self) -> None:
        self.log.info(f"Online on user {self.user.name}\n{round(self.latency*100)} ms.")
        await self.delta_activity()
    

    async def delta_activity(self):
        activity = discord.Streaming(name='d.help', url='https://twitch.tv/glz007', game='Discord')
        await self.change_presence(status=discord.Status.online if not self.maintenance else discord.Status.dnd, activity=activity)
    
    
    @property
    def mongo(self) -> c.Mongo:
        return self.get_cog("Mongo")
    
    @property
    def auto_delete(self) -> c.AutoDelete:
        return c.AutoDelete(self)
    
    @property
    def auto_purge(self) -> c.AutoPurge:
        return c.AutoPurge(self)
    
    
    def setup_logging(self):
        logging.basicConfig(
            handlers=[
                logging.StreamHandler(sys.stdout)
            ],
            format=f"{Fore.MAGENTA}%(asctime)s {Fore.RED}[%(levelname)s]{Fore.RESET} - {Fore.YELLOW}%(message)s{Fore.RESET}",
            datefmt="%d/%m/%Y %H:%M:%S",
            level=logging.INFO
        )
        self.log = logging.getLogger(__name__)

    
    
if __name__ == '__main__':
    Delta()
    
    
    