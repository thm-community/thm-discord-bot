import json
import requests
import random

import aiohttp
import discord
from discord.ext import commands

import libs.config as config
from libs.embedmaker import officialEmbed
from libs.utils import api_fetch


class Fun(commands.Cog, name="Fun Commands"):
    def __init__(self, bot):
        self.bot = bot

    ###################################
    ### Skidy, Ashu, Dark's quotes. ###
    ###################################

    @commands.command(description="Sends Skidy's emote.")
    async def skidy(self, ctx):

        message = ":slight_smile:"

        if random.randint(0,1) >= 0.5:
            skidy_gif = self.bot.get_emoji(config.get_config("emotes")["skidygif"])
            message = str(skidy_gif)            


        response = officialEmbed(title=message, color=0x225999,
                                 author="Skidy", author_img="https://i.imgur.com/fSMnXPt.png", footer="")
        await ctx.send(embed=response)

    @commands.command(description="Send Ashu's emote.")
    async def ashu(self, ctx):
        response = officialEmbed(title=":slight_smile:", color=0x225999,
                                 author="Ashu", author_img="https://i.imgur.com/ojiqdem.png", footer="")
        await ctx.send(embed=response)

    @commands.command(description="Send a random Darkstar quote.")
    async def dark(self, ctx):
        darkQuotes = config.get_string("quotes")["dark"]
        quote = darkQuotes[random.randint(0, len(darkQuotes)-1)]

        if quote == "buttdance":
            buttdance = self.bot.get_emoji(config.get_config("emotes")["buttdance"])
            quote = str(buttdance)

        response = officialEmbed(title=quote, color=0xff4500, author="DarkStar7471",
                                 author_img="https://i.imgur.com/jZ908d1.png", footer="")
        await ctx.send(embed=response)

    ########################
    ### HONK, BOOP, NOOT ###
    ########################

    @commands.command(description="HOOONK!")
    async def honk(self, ctx):
        response = officialEmbed("***HONK HONK HONK***", color=0xff4500)
        response.set_image(
            url="https://cdn.discordapp.com/attachments/433685563674198016/630100135623524363/JPEG_20191003_021216.jpg")
        await ctx.send(embed=response)

    @commands.command(description="Boop someone!", usage="{@user}")
    async def boop(self, ctx, member: discord.Member):
        desc = "<@{}> was booped by <@{}>!".format(member.id, ctx.author.id)
        response = officialEmbed("!boop", desc, color=0xFFFFFF)
        response.set_image(url="http://giphygifs.s3.amazonaws.com/media/99LhY1qc6jG8w/giphy.gif")

        await ctx.send(embed=response)

    @commands.command(description="NOOT NOOT!")
    async def noot(self,ctx):
        response = officialEmbed("NOOT NOOT", color=0xffffff)
        response.set_image(url="https://media1.tenor.com/images/3be64f537ae5dc421d7a8580c1fcde7c/tenor.gif?itemid=15674396")

        await ctx.send(embed=response)

    ###############
    ### COOCTUS ###
    ###############

    @commands.command(description="COOCTUS!")
    async def cooctus(self,ctx):
        response = officialEmbed("It's cooctus time!", color=0xffffff)
        response.set_image(
            url="https://i.imgur.com/t5UD8iB.png")

        await ctx.send(embed=response)

    ########################
    ### Shiba And Spaniel###
    ########################
    @commands.command(description="Sends a shibe picture.")
    async def shibe(self, ctx):
        response = officialEmbed("Shiba Inu", color=0xff4500, footer="Images from dog.ceo ❤")
        response.set_image(url=self._get_dog_image("shiba"))
        await ctx.send(embed=response)

    @commands.command(description="Sends a spaniel picture.")
    async def spaniel(self, ctx):
        response = officialEmbed("Spaniel", color=0xff4500, footer="Images from dog.ceo ❤")
        response.set_image(url=self._get_dog_image("spaniel"))
        await ctx.send(embed=response)
        
    @commands.command(description="Sends a Ollie picture.")
    async def ollie(self, ctx):
        response = officialEmbed("Ollie", color=0xff4500, footer="Ollie Unix Montgomery")
        response.set_image(url=_get_ollie_image)
        await ctx.send(embed=response)

    @staticmethod
    def _get_dog_image(breed):
        r = requests.get(f"https://dog.ceo/api/breed/{breed}/images/random") # spaniel, shiba
        return json.loads(r.text)["message"]
        
    def _get_ollie_image:
        r = requests.get(f"http://ollie.muirlandoracle.co.uk") # ollie
        return json.loads(r.text)["message"]

    ############
    ### XKCD ###
    ############

    @commands.command(description="Send a random XKCD comic.")
    async def xkcd(self, ctx):
        comic_no = random.randint(1, 1900)
        url = f"http://xkcd.com/{comic_no}/info.0.json"
        data = await api_fetch(url)

        img = data.get("img")
        title = data.get("title")
        alt = data.get("alt")

        response = officialEmbed(color=0xffb6b9, footer="From the XKCD Official API!")
        response.add_field(name=title, value=alt)
        response.set_image(url=img)

        await ctx.send(embed=response)


def setup(bot):
    bot.add_cog(Fun(bot))
