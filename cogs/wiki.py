import discord 
import asyncio 
import aiohttp
import json
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # Getting the query from Wiki's oficial API.
    @commands.command()
    async def wiki(self,ctx,*,search):
        try:
            api_url = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles="+search
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as data:
                    # Request.
                    data = await data.read()
                    data = json.loads(data)['query']['pages']
                    data = next(iter(data.values()))
                    
                    # Get the data.
                    title = data['title']
                    content = data['extract'].split(".")
                    
                    # Embed.
                    response = discord.Embed(color=0xffffff)
                    response.add_field(name=title,value=''.join(content[:2]))
                    response.set_author(name="TryHackMe",icon_url="https://tryhackme.com/img/THMlogo.png")
                    response.set_footer(text="From the Wikipedia Official API!")
            
            await ctx.send(embed=response)
        except:
            await ctx.send("Some Error Occured!")

def setup(bot):
    bot.add_cog(Utility(bot))