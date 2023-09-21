from datetime import datetime
from dateutil import tz 
import secrets, string

def now_time() -> str:
    return int(datetime.now(tz=tz.gettz("America/Sao_Paulo")).timestamp())


def random_id():
    a = string.ascii_letters + string.digits
    return ''.join(secrets.choice(a.lower()) for i in range(10))

