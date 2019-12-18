import discord
from discord.ext import commands
import json


class Gtfobins(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def gtfobins(self, ctx, search_term=""):
        gtfobins_file = json.loads(open("config/gtfobins.json", "r").read())
        print(search_term)
        if search_term  != "":
            try:
                data = gtfobins_file[search_term]
                response = discord.Embed(title="Gtfobins' {} results:-".format(search_term), color=0xcc0000)
                result = "".join(["- " + item + "\n" for item in data])
                response.set_thumbnail(url="https://gtfobins.github.io/assets/logo.png")
                response.add_field(name="Search_term: ", value=search_term)
                response.add_field(name="Vulnerabilities: ", value=result)
                response.add_field(name="URL: ", value="https://gtfobins.github.io/gtfobins/"+search_term)
                await ctx.send(embed=response)
            except Exception as e:
                await ctx.send("{} not found in gtfobins.".format(search_term))
        else:
            try:
                result = ""
                for key, value in gtfobins_file.items():
                    result += "- " + key
                    result += "\n"
                response = discord.Embed(title="Gtfobins binaries:-\n", color=0xcc0000)
                response.set_thumbnail(url="https://gtfobins.github.io/assets/logo.png")
                response.add_field(name="List of binaries:\n", value=result)
                response.add_field(name="Search vulnerability of specific binary by using !gtfobins <name>")
                await ctx.send("Sending the whole list....")
                await ctx.send(embed=response)
            except Exception as e:
                await ctx.send("Something went wrong!")

def setup(bot):
    bot.add_cog(Gtfobins(bot))