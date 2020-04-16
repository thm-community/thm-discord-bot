import discord
import aiohttp
import asyncio
import json
from discord.utils import get
from discord.ext import commands
from discord import guild
from discord.channel import DMChannel

# IDs.
guildF = json.loads(open("config/guild.json", "r").read())
rolesF = json.loads(open("config/roles.json", "r").read())

guildID = guildF["server"]
rolesID = rolesF["ranks"]
subID = rolesF["sub"]
contribID = rolesF["contrib"]


## Message managment.
async def deleteCommand(ctx):
        await ctx.send("Updating roles for " + ctx.message.author.mention + "!")
        await ctx.bot.delete_message(ctx.message)


## Role managment.
def hasRole(member, id):
        for role in member.roles:
                if id == role.id:
                        return True
        return False

async def removeLevelRoles(member):
        for rId in rolesID:
                if hasRole(member, rId):
                        await member.remove_roles(get(member.guild.roles, id=rId))

async def removeSubRole(member):
        await member.remove_roles(get(member.guild.roles, id=subID))

async def removeContribRole(member):
        await member.remove_roles(get(member.guild.roles, id=contribID))

async def addRole(member, id):
        await member.add_roles(get(member.guild.roles, id=id))


## Actual command.
class RoleSync(commands.Cog,name="Verifying/Role Assigning Commands"):
        def __init__(self,bot):
                self.bot = bot

        @commands.command(description="Verify yourself to get your roles.", usage="{token}")
        async def verify(self, ctx, userToken=None):

                # If not DM, clear the message so that the token isn't kept publicly.
                if not isinstance(ctx.channel, DMChannel):
                        await ctx.message.delete()
                        msg = await ctx.send("Please send that command to the bot in a DM. This is to stop other people from using using your token :slight_smile:")
                        await asyncio.sleep(15)
                        await msg.delete()
                        return

                # If no token sends message...
                if userToken == None:
                        await ctx.send("Usage: !verify <token>\nGet your token from https://tryhackme.com/profile.")
                        return
                # Otherwise, keeps going:
                else:
                        async with aiohttp.ClientSession() as session:
                                async with session.get("https://tryhackme.com/tokens/discord/" + userToken) as data:

                                        cmdResult = ""

                                        data = await data.read()
                                        success = json.loads(data)["success"]

                                        if success == False:
                                                cmdResult = "I'm sorry but I couldn't find the specified token!"
                                        else:
                                                server = self.bot.get_guild(guildID)

                                                # If server ID is wrong.
                                                if server == None:
                                                        await ctx.send("An unexpected error has occured. Please contact THM's BOT maintainers.\nERROR: Server not found.")
                                                        return

                                                user = ctx.message.author
                                                member = server.get_member(user.id)

                                                # If user isn't a member or wrong.
                                                if user == None or member == None:
                                                        await ctx.send("An unexpected error has occured. Please contact THM's BOT maintainers.\nERROR: User not found.")
                                                        return

                                                level = json.loads(data)["level"] - 1
                                                sub = json.loads(data)["subscribed"]

                                                # Special case: Contributors.
                                                if level == 997:
                                                        if not hasRole(member, contribID):
                                                                await removeLevelRoles(member)
                                                                await addRole(member, contribID)
                                                                cmdResult += "You are now a contributor, thanks!\n"
                                                        else:
                                                                cmdResult += "Your level is already up-to-date.\n"
                                                if level != 997 and hasRole(member, contribID):
                                                        await removeContribRole(member)
                                                        cmdResult += "You are no longer a contributor.\n"

                                                # Normal ranks.
                                                if level < len(rolesID):
                                                        if not hasRole(member, rolesID[level]):
                                                                await removeLevelRoles(member)
                                                                await addRole(member, rolesID[level])
                                                                cmdResult += "Your level has been updated!\n"
                                                        else:
                                                                cmdResult += "Your level is already up-to-date.\n"

						# Checks for the users' sub status.
                                                if sub == 0:
                                                        if hasRole(member, subID):
                                                                await removeSubRole(member)
                                                                cmdResult += "You are not longer a subscriber!"
                                                else:
                                                        if not hasRole(member, subID):
                                                                await addRole(member, subID)
                                                                cmdResult += "You are now a subscriber, thanks!"
                                        
                                        await ctx.send(cmdResult)
            

def setup(bot):
        bot.add_cog(RoleSync(bot))
