from datetime import datetime
from dateutil import tz 
import secrets, string
import json 


def now_time() -> str:
    return int(datetime.now(tz=tz.gettz("America/Sao_Paulo")).timestamp())


def random_id():
    a = string.ascii_letters + string.digits
    return ''.join(secrets.choice(a.lower()) for i in range(10))


class Emoji:
    pass 


class Emotes:
        
    def __init__(self) -> None:
        
        with open('./helpers/emojis.json', 'r', encoding='utf-8') as f:
            emojis = json.load(f)
            
        self.uni, self.custom = emojis.items()
    
    
    @property
    def smiley(self) -> Emoji:
        return self.uni[1]['smiley']
    
    
    @property
    def sunglasses(self) -> Emoji:
        return self.uni[1]['sunglasses']
    
    
    @property
    def nhe(self) -> Emoji:
        return self.uni[1]['nhe']
    
    
    @property
    def you(self) -> Emoji:
        return self.uni[1]['you']
    
    @property
    def  thumbsup(self) -> Emoji:
        return self.uni[1]['thumbsup']
    
    ## Custom 
    
    @property
    def python(self) -> Emoji:
        return self.custom[1]['python']

    
    @property
    def audit(self) -> Emoji:
        return self.custom[1]['audit_log']
    
    
    @property
    def owner(self) -> Emoji:
        return self.custom[1]['owner_logo']
    
    
    @property
    def info(self) -> Emoji:
        return self.custom[1]['info']


    @property
    def banned(self) -> Emoji:
        return self.custom[1].get("banned_user")
    
    @property
    def kick(self) -> Emoji:
        return self.custom[1].get("kick")


    @property
    def purge(self) -> Emoji:
        return self.custom[1].get("purge")
    
    @property
    def delete(self) -> Emoji:
        return self.custom[1].get("delete")