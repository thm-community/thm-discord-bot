from discord.ext import commands
import discord, random, time, asyncio, requests, json,tweepy
from libs.embedmaker import officialEmbed

#URL to Docs Subdomain
docsURL = "https://docs.tryhackme.com/"

#
docsTitle = "The URL of TryHackme's Documentation"

## Pictures.
docsPic = "https://docs.tryhackme.com/img/thm-favicon.png"

## Colors
docsColor = 0xd9534f

def getEmbedDocs(n, v, t, c):
    response = officialEmbed(n,v, color=c)
    response.set_thumbnail(url=t)
    return response

class docs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Get the bot's Docs link.")
    async def docs(self, ctx):
        response = getEmbedSocial(docsTitle, docsURL, docsPic, docsColor)
        await ctx.send(embed=response)