from discord.ext import commands 
from datetime import datetime
from datetime import timedelta
from dateutil import tz
import typing
import discord
import re

class DateConverter(commands.Converter):

    async def convert(self, ctx: commands.Context, arg: str) -> timedelta:

        mult = {
            "ms": 1000,
            "s": 1,
            "m": 60,
            "h": 3600,
            "d": 86400,
            "w": 604800
        }

        try:

            amt = int(arg[:-1])
            unit = arg[-1]

            seconds = amt * mult[unit]
            date = timedelta(seconds=seconds)
            return date 
        except (KeyError, ValueError):
            raise commands.BadArgument("Duração inserida é inválida.") 


class MassBanConverter(commands.Converter):

    async def convert(self, ctx: commands.Context, *arg) -> typing.List[discord.User]:
        
        users = [re.sub(r"[^<>@.-=*/!$%¨&*()]", "", x).strip() for x in arg[0].split(",")]
        returns = []
        not_returns = 0 


        for user in users:

            try:
                
                returns.append(await ctx.guild.fetch_member(int(user)))
            
            except (KeyError, discord.NotFound, ValueError):
                not_returns += 1
                continue;

        return [returns, not_returns]



    
    