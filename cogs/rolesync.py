import asyncio
import json
import time

import aiohttp
import discord
from discord import guild
from discord.channel import DMChannel
from discord.ext import commands
from discord.utils import get

import libs.config as config
import libs.database as database
from libs.utils import api_fetch, has_role, add_role
from libs.embedmaker import officialEmbed

### Hello, this is Horshark. 
### Before you all @ me, I know. This is disgusting code.
### The update() function should be cleaner.
### The code in verify and the autoupdater can be factorized into the update() function.
### If you are reading this, there probably is an issue about this.
### Sorry for the new pair of glasses you will need.
### Have a good day.
###
### PS: It is planned to eventually rework this.
### PS 2: You can find me on Discord and I'll try to help.


####################
# Config variables #
####################

c_sleeptime = config.get_config("sleep_time")["roles_update"]
c_api_token = config.get_config("url")["api"]["token"]


#####################
# Strings variables #
#####################

s_verify = config.get_string("verify")
s_verify_del = config.get_string("verify_delete")


###################
# Other variables #
###################

id_guild = config.get_config("server")

roles = config.get_config("roles")
id_admin = roles["admin"]
id_mod = roles["mod"]
id_ranks = roles["ranks"]
id_sub = roles["sub"]
id_contrib = roles["contrib"]
id_verified = roles["verified"]
id_bughunter = roles["bughunter"]

# DB
db = database.connect_to_db()


#############
# Functions #
#############

# Role managment.
async def remove_rank_roles(member):
    """Remove the member's rank/level roles."""

    for rId in id_ranks:
        if has_role(member, rId):
            await member.remove_roles(get(member.guild.roles, id=rId))

async def remove_sub_role(member):
    """Removes the member's sub role."""

    await member.remove_roles(get(member.guild.roles, id=id_sub))

async def remove_contrib_role(member):
    """Remove the user's contrib role."""

    await member.remove_roles(get(member.guild.roles, id=id_contrib))

async def remove_bughunter_role(member):
    """Remove the user's bughunter role."""

    await member.remove_roles(get(member.guild.roles, id=id_bughunter))


async def remove_verified_role(member):
    """Remove the user's verified role."""

    await member.remove_roles(get(member.guild.roles, id=id_verified))

# Update a member's roles.
async def update(member, dm, data, skipUpdatedMessage = False):
    """Updates the user's roles."""

    cmdResult = ""

    level = data["level"] - 1
    sub = data["subscribed"]

    # Special case: Contributors.
    if level == 997:
        if not has_role(member, id_contrib):
            await remove_rank_roles(member)
            await add_role(member, id_contrib)
            cmdResult += s_verify["contrib_add"] + "\n"

    if level != 997 and has_role(member, id_contrib):
        await remove_contrib_role(member)
        cmdResult += s_verify["contrib_remove"] + "\n"

    # Special case: Bug Hunter
    if level == 998:
        if not has_role(member, id_bughunter):
            await remove_rank_roles(member)
            await add_role(member, id_bughunter)
            cmdResult += s_verify["bughunter_add"] + "\n"

    if level != 998 and has_role(member, id_bughunter):
        await remove_bughunter_role(member)
        cmdResult += s_verify["bughunter_remove"] + "\n"

    # Normal ranks.
    if level < len(id_ranks):
        if not has_role(member, id_ranks[level]):
            await remove_rank_roles(member)
            await add_role(member, id_ranks[level])

            cmdResult += s_verify["level_updated"] + "\n"
        elif not skipUpdatedMessage:
                cmdResult += s_verify["level_up-to-date"] + "\n"

    # Checks for the users' sub status.
    if sub == 0:
        if has_role(member, id_sub):
            await remove_sub_role(member)
            cmdResult += s_verify["sub_remove"] + "\n"
    else:
        if not has_role(member, id_sub):
            await add_role(member, id_sub)
            cmdResult += s_verify["sub_added"] + "\n"
    
    # Checks if the users has the verified role.
    if not has_role(member, id_verified):
        await add_role(member, id_verified)
        cmdResult += s_verify["verified_added"] + "\n"

    if cmdResult != "":
        try:
            await dm.send(cmdResult)
        except:
            print("\t{} has blocked DMs.".format(member))


############
# COG Body #
############

class RoleSync(commands.Cog, name="Verifying/Role Assigning Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description=s_verify["help_desc"], usage="{token}")
    async def verify(self, ctx, input_token=None):

        # If not DM, clear the message so that the token isn't kept publicly.
        if not isinstance(ctx.channel, DMChannel):
            await ctx.message.delete()

            msg = await ctx.send(s_verify["error_not_dm"])
            time.sleep(15)
            await msg.delete()

            return

        # If no token sends message...
        if input_token == None:
            await ctx.send(s_verify["usage"])
            return
        
        # Otherwise, keeps going:
        else:
            cmdResult = ""  

            data = await api_fetch(c_api_token, input_token)
            success = data["success"]

            # If the token isn't valid.
            if success == False:
                cmdResult = s_verify["token_not_found"]
                await ctx.send(cmdResult)
            else:
                ### Verifies that the token is being use only once and that the discord account doesn't have multiple tokens. ###
                
                # If user already has got a token (the provided token and one found are different)
                user_tokens = database.get_user_by_discord_uid(db, ctx.author.id)

                if len(user_tokens) > 0 and not user_tokens[0][1] == input_token:
                    cmdResult = s_verify["already_verified"]
                    
                    channel = discord.utils.get(guild.text_channels, name="staff_lounge")
                    embed = officialEmbed("Alert! Re-verification detected!")
                    
                    timestamp = datetime.now()
                    embed.add_field(name="Username: ", value="{}".format(ctx.author), inline=False)
                    embed.add_field(name="User ID:", value=' '.join(ctx.author.id), inline=False)
                    embed.add_field(name="Timestamp:", value=timestamp, inline=False)
                    
                    await channel.send(embed=embed)


                    await ctx.send(cmdResult)
                    return    

                # If the token is already used
                token_accounts = database.get_user_by_thm_token(db, input_token)

                if len(token_accounts) > 0 and not token_accounts[0][0] == str(ctx.author.id):
                    cmdResult = s_verify["token_in_use"]

                    await ctx.send(cmdResult)
                    return    


                ### Retrieves needed variables and updates DB if needed. ###

                # If server ID is wrong.
                server = self.bot.get_guild(id_guild)
                
                if server == None:
                    await ctx.send(s_verify["error"] + "ERROR: Server not found.")
                    return
                
                # If user isn't a member.
                user = ctx.message.author
                member = await server.fetch_member(user.id)

                if member == None:
                    database.remove_user_by_discord_uid(db, ctx.author.id)
                    await ctx.send(s_verify["not_a_member"])
                    return

                dm_channel = await member.create_dm()

                result = database.get_user_by_thm_token(db, input_token)

                # If user is not in DB; add him.
                if len(result) == 0:
                    database.add_user(db, member.id, input_token)

                ### Updates roles for the user. ###
                await update(member, dm_channel, data)

    @commands.command(name="tokenremove", description=s_verify_del["help_desc"] + " (Admin, Mod)", usage="{@user}", hidden=True)
    async def remove_token(self, ctx, uid):

        if has_role(ctx.author, id_admin) or has_role(ctx.author, id_mod):
            # Removes the user from the DB.
            database.remove_user_by_discord_uid(db, uid)
            msg = s_verify_del["done"].format(uid)
            
            # TODO: Add member fetching, if not null:
            # Removes the user's roles (verified, sub, contrib, rank..)
            #await remove_verified_role(member)
            #await remove_sub_role(member)
            #await remove_rank_roles(member)
            #await remove_contrib_role(member)

            await ctx.send(msg)

    # The function that when called, update every user in the DB.
    async def auto_updater(self):
        """Function that runs constantly to ensure the roles are automaticallyupdated.."""

        ### Retrieves needed variables and updates DB if needed. ###
        server = self.bot.get_guild(id_guild)

        # If server ID is wrong.
        if server == None:
            print(s_verify["error"] + "ERROR: Server not found. (auto updater)")
            return
            
        while True:
            # Logging.
            print("\n---- Updating roles:")

            # We retrieve all users from DB.
            users = database.get_user_all(db)

            for user in users:
                # User's Discord UID and THM token.
                user_dUID = user[0]
                user_thm = user[1]

                # We try to fetch the user.
                try:
                    user_member = await server.fetch_member(user_dUID)

                    # Logging.
                    user_thm_censored = user_thm[:3] + '*'*18 + user_thm[-3:]
                    print("\t" + user_member.name + " | " + user_dUID + ", " + user_thm_censored)

                    # Getting his data.
                    data = await api_fetch(c_api_token, user_thm)

                    # Getting the DM channel and calling update function.
                    dm_channel = await user_member.create_dm()
                    await update(user_member, dm_channel, data, True)

                except:
                    print("\tUser " + user_dUID + " has left the server.")

                
            print("-- Role updating finished.\n")

            await asyncio.sleep(c_sleeptime)

    # Starts the auto update.
    @commands.Cog.listener()
    async def on_ready(self):
        await self.auto_updater()

def setup(bot):
    bot.add_cog(RoleSync(bot))
