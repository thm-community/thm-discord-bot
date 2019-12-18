from discord.ext import commands
import discord
import json
import random
import aiohttp


class Fun(commands.Cog, name="Fun Commands"):
    def __init__(self, bot):
        self.bot = bot


    ###################################
    ### Skidy, Ashu, Dark's quotes. ###
    ###################################

    @commands.command()
    async def skidy(self, ctx):
        response = discord.Embed(title=":slight_smile:", description="", color=0x225999)
        response.set_author(name="Skidy",icon_url="https://i.imgur.com/fSMnXPt.png")
        await ctx.send(embed=response)

    @commands.command()
    async def ashu(self, ctx):
        response = discord.Embed(title=":slight_smile:", description="", color=0x225999)
        response.set_author(name="Ashu",icon_url="https://i.imgur.com/ojiqdem.png")
        await ctx.send(embed=response)

    @commands.command()
    async def dark(self, ctx):
        darkF = json.loads(open("config/dark.json", "r").read())
        darkQuotes = darkF["quotes"]

        response = discord.Embed(title=darkQuotes[random.randint(0, len(darkQuotes)-1)], description="", color=0xff4500)
        response.set_author(name="DarkStar7471",icon_url="https://i.imgur.com/jZ908d1.png")
        await ctx.send(embed=response)


    #####################
    ### HONK and BOOP ###
    #####################

    @commands.command()
    async def honk(self, ctx):
        response = discord.Embed(title="!honk", description="***HONK HONK HONK***", color=0xff4500)
        response.set_author(name="TryHackMe",icon_url="https://tryhackme.com/img/THMlogo.png")
        response.set_image(url="https://cdn.discordapp.com/attachments/433685563674198016/630100135623524363/JPEG_20191003_021216.jpg")
        await ctx.send(embed=response)
    
    @commands.command()
    async def boop(self, ctx, member: discord.Member=None):
        if ctx.message.channel.name == "bot-commands" and member is not None:
                if member.id == 572908911749890053: #Yume - Asphodel#8097 572908911749890053
                    desc = "<@{}>, you can't boop <@{}>!".format(ctx.author.id, member.id)
                    response = discord.Embed(title="!boop", description=desc, color=0xFFFFFF)
                    response.set_author(name="TryHackMe",icon_url="https://tryhackme.com/img/THMlogo.png")
                else:
                    desc = "<@{}> was booped by <@{}>!".format(member.id, ctx.author.id)
                    response = discord.Embed(title="!boop", description=desc, color=0xFFFFFF)
                    response.set_author(name="TryHackMe",icon_url="https://tryhackme.com/img/THMlogo.png")
                    response.set_image(url="http://giphygifs.s3.amazonaws.com/media/99LhY1qc6jG8w/giphy.gif")
                await ctx.send(embed=response)
        else:
            return


    ############
    ### XKCD ###
    ############

    @commands.command()
    async def xkcd(self,ctx):
        comic_no = random.randint(1,1900)
        url = f"http://xkcd.com/{comic_no}/info.0.json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as data:
                new_data = await data.read()
                json_data = json.loads(new_data)
                img = json_data.get("img")
                title = json_data.get("title")
                alt = json_data.get("alt")
                response = discord.Embed(color=0xffb6b9)
                response.add_field(name=title,value=alt)
                response.set_image(url=img)
                response.set_author(name="TryHackMe",icon_url="https://tryhackme.com/img/THMlogo.png")
                response.set_footer(text="From the XKCD Official API!")
        await ctx.send(embed=response)
            


def setup(bot):
    bot.add_cog(Fun(bot))        