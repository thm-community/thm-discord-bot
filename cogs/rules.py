import discord
import aiohttp
import asyncio
import json
from discord.ext import commands

class Rules(commands.Cog,name="Rank Commands"):
        def __init__(self,bot):
                self.bot = bot

        @commands.command()
        async def rules(self,ctx):
                # Make embed.
                response = discord.Embed(title="Rules", color=0xffff00)
                response.set_author(name="TryHackMe",icon_url="https://tryhackme.com/img/THMlogo.png")
                response.set_thumbnail(url="https://tryhackme.com/img/THMlogo.png")
                
                # Load the rules from config.
                rulesF = json.loads(open("config/rules.json", "r").read())
                rules = rulesF["rules"]
                i = 0

                # Add each rule.
                for rule in rules:
                        response.add_field(name=(str(i+1)+"."), value=rule)
                        i = i + 1

                response.set_footer(text="From the TryHackMe Official API!")
                
                # Send.
                await ctx.send(embed=response)

def setup(bot):
        bot.add_cog(Rules(bot))
