import discord
import aiohttp
import asyncio
import json
from discord.ext import commands
import requests
from requests.exceptions import HTTPError
import random

from libs.embedmaker import officialEmbed

quotes = [
    "C4n y0u pwn th4 m4chin3?",
    "Hacker man 0x1 0x0 0x1",
    "The quieter you become the more you are able to hear",
    "\*Morpheus\*: Red or Blue pill?",
    "Access security... Access security grid... YOU DIDN'T SAY THE MAGIC WORD!",
    "Just hack the mainframe.",
    "Z2VsdW5weHpyLnBieg==",
    "The Matrix is real",
    "No place like 127.0.0.1",
    "Hack the planet",
    "Just obfuscate it...",
    "Armitage + Hail Mary",
    "WEP, WPA, WAH?",
    "admin:password",
    "rockyou.txt",
    "tmux > screens",
    "tabs or spaces?",
    "Leeerrrroy Jeekinnnns...",
    "Enumeration is key",
    "Try harder..",
    "https://discord.gg/zGdzUad",
    "Satoshi Nakamoto",
    "Mining Bitcoin...",
    "Configuring neural network"
    ]

def getMoto():
    return quotes[random.randint(0, len(quotes) - 1)]

# Getting infos.
def getAvatars(username):
    response = requests.get("https://tryhackme.com/api/user/{}".format(username))
    data = response.text
    data = json.loads(data)
    return data['avatar']
    
def getPoints(username):
    response = requests.get("https://tryhackme.com/api/user/{}".format(username))
    data = response.text
    data = json.loads(data)
    return data['points']

def getRank(username):
    response = requests.get("https://tryhackme.com/api/user/{}".format(username))
    data = response.text
    data = json.loads(data)
    return data['userRank']


def getSubStatus(username):
    url = "https://tryhackme.com/p/{}".format(username)
    check = "No!"
    try:
        response = requests.get(url)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        #print(response.text)
        if "<span>Subscribed</span>" in response.text:
            check = "Yes!"
        else:
            check = "No!"
    return check

def sanitize_check(data):
    chars = ["/",";","-",">","<",":","`","'\"","|"]
    if any((c in chars) for c in data):
        return True
    else:
        return False


class Userrank(commands.Cog,name="Rank Commands"):
    def __init__(self,bot):
        self.bot = bot

    @commands.command(description="Get a THM member's rank.", usage="{username}")
    async def rank(self,ctx,*,user):
	    if user == None:
	        return await ctx.send("You must specify a username for this command!")

        if sanitize_check(user) == True:
            return await ctx.send("Sorry, the characters you have entered are blacklisted, instead of trying anything here, try some rooms.")
            
        async with ctx.channel.typing():
            message = await ctx.send(f"Fetching {user}'s rank...")
            try:
                if getRank(user) != 0:
                    quip = getMoto()
                    quip = "*{}*".format(quip)
                    
                    userImg = getAvatars(user)
                    Points = getPoints(user)
                    rank = getRank(user)

                    response = officialEmbed("!rank", quip, 0x148f77)
                    
                    response.set_thumbnail(url=userImg)
                    response.add_field(name="Username:", value=user, inline=True)
                    response.add_field(name="Rank:", value= rank, inline=True)
                    response.add_field(name="Points:", value=Points, inline=True)
                    
                    sub = getSubStatus(user)
                    
                    response.add_field(name="Subscribed?", value=sub, inline=True)
                else:
                    quip = getMoto()
                    quip = "*{}*".format(quip)

                    response = officialEmbed("!rank", quip, 0xdc143c)

                    userImg = "https://tryhackme.com/img/favicon.png"
                    
                    response.set_thumbnail(url=userImg)
                    response.add_field(name="Username:", value=user, inline=True)
                    response.add_field(name="Rank:", value="**Error: Username Not Found!**", inline=True)
                            
                await message.edit(content=None, embed=response)
            except:
                await message.edit(content="**An issue has occured.**")
        
def setup(bot):
	bot.add_cog(Userrank(bot))
