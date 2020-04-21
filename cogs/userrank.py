from discord.ext import commands
import random

from libs.embedmaker import officialEmbed
import libs.thm_api as thm

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


def sanitize_check(data):
    chars = ["/", ";", "-", ">", "<", ":", "`", "'\"", "|"]
    if any((c in chars) for c in data):
        return True
    else:
        return False


class Userrank(commands.Cog, name="Rank Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Get a THM member's rank.", usage="{username}")
    async def rank(self, ctx, *, user):
        if sanitize_check(user):
            await ctx.send(
                "Sorry, the characters you have entered are blacklisted, instead of trying anything here, try some rooms.")
        else:
            try:
                user_data = thm.getUserData(user)

                if user_data['userRank'] != 0:
                    quip = getMoto()
                    quip = "*{}*".format(quip)

                    response = officialEmbed("!rank", quip, 0x148f77)

                    response.set_thumbnail(url=user_data['avatar'])
                    response.add_field(name="Username:", value=user_data['avatar'], inline=True)
                    response.add_field(name="Rank:", value=user_data['userRank'], inline=True)
                    response.add_field(name="Points:", value=user_data['points'], inline=True)

                    sub = thm.isSubscribed(user)

                    response.add_field(name="Subscribed?", value=sub, inline=True)
                else:
                    quip = getMoto()
                    quip = "*{}*".format(quip)

                    response = officialEmbed("!rank", quip, 0xdc143c)

                    user_img = "https://tryhackme.com/img/favicon.png"

                    response.set_thumbnail(url=user_img)
                    response.add_field(name="Username:", value=user, inline=True)
                    response.add_field(name="Rank:", value="**Error: Username Not Found!**", inline=True)

                await ctx.send(embed=response)
            except:
                await ctx.send("**An issue has occured.**")


def setup(bot):
    bot.add_cog(Userrank(bot))
