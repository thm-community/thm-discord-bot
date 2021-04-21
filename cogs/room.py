"""Rooms Cog
Cog to handle room lookup and details related to them.
Also handles the automatic announcement of a new room from TryHackMe

User Usage:
writeup [room code]
randomroom

Admin Only:
room - manually announce last announced room
newroom [room code] - manually announce a new room via room code
"""

import asyncio
import json
import time
from shutil import copyfile
from random import choice

import aiohttp
import discord
from discord.ext import commands

import libs.config as config
from libs.command_manager import check
from libs.embedmaker import officialEmbed
from libs.utils import api_fetch, has_role, bool_to_yesno
from libs.thm_api import get_public_rooms
from libs.utils import sanitize_check


####################
# Config variables #
####################

c_room_data = config.get_config("data_files")["room"]
c_room_default_data = config.get_config("data_files")["room_default"]
c_sleep_time = config.get_config("sleep_time")["room_listener"]
c_api_url = config.get_config("url")["api"]
c_url_room = config.get_config("url")["room"]
c_join_room = config.get_config("url")["room_join"]

#####################
# Strings variables #
#####################

s_no_perm = config.get_string("commands")["no_perm"]
s_room = config.get_string("room")


###################
# Other variables #
###################

# Channel ID.
id_channels = config.get_config("channels")
id_channel = id_channels["announcements"]

# Role IDs.
id_admin = config.get_config("roles")["admin"]
id_announcerole = config.get_config("roles")["announcementrole"]


#############
# Functions #
#############

# Sending announcement function.
async def announce_room(channel, json_data, code=None):
    """Announces a room using its data."""

    print(json_data)
    print(json_data['image'])

    # Set up embed.
    img = json_data["image"]
    title = json_data["title"]
    if code == None:
        url = c_join_room + str(json_data["code"])
    else:
        url = c_join_room + code
    description = json_data["description"]

    embed = officialEmbed(title, description)
    embed.set_image(url=img)

    # Get the announcement role.
    announceRole = channel.guild.get_role(id_announcerole)

    # Send messages.
    await channel.send(s_room["newroom"].format(url, announceRole.mention), embed=embed)

    roomCategory = discord.utils.get(channel.guild.categories, name="Recent Releases Help")

    # Create new room channel.
    roomChannel = await channel.guild.create_text_channel(json_data["title"], category=roomCategory)
    await roomChannel.edit(topic=url)
 
    # Updates local file.
    with open(c_room_data, "w") as file:
        json.dump(json_data, file)


def get_random_room():
    rooms = get_public_rooms()

    return choice(rooms)


############
# COG Body #
############

class Room(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description=s_room["writeup_help_desc"], usage="{room_code}")
    async def writeup(self, ctx, room_code):
        if not sanitize_check(room_code):
            return

        # Request to the API.
        data = await api_fetch(c_api_url["room"].format(room_code))

        # If the specified code is wrong.
        if data[room_code]["success"] == False:
            botMsg = await ctx.send(s_room["code_not_found"].format(room_code))

            await asyncio.sleep(5)
            await botMsg.delete()
            await ctx.message.delete()

            return

        # If there is no writeup.
        if len(data[room_code]["writeups"]) == 0:
            await ctx.send(s_room["writeup_not_found"])
            return

        # Set up embed.
        img = data[room_code]["image"]
        title = data[room_code]["title"]
        link = c_url_room + room_code

        embed = officialEmbed(title, link)
        embed.set_image(url=img)

        for item in data[room_code]["writeups"]:
            embed.add_field(
                name="By: "+item["username"], value=item["link"])

        # Send messages.
        await ctx.send(embed=embed)

    @commands.command(description=s_room["room_help_desc"] + " (Admin, LeadMod)", hidden=True)
    @check(roles=["modlead", "admin"], dm_flag=False)
    async def room(self, ctx):
        # Gets channel.
        channel = self.bot.get_channel(id_channel)

        # Getting the API's JSON.
        data = await api_fetch(c_api_url["newrooms"])

        await announce_room(channel, data[0])

    @commands.command(name="newroom", description=s_room["newroom_help_desc"] + " (Admin, LeadMod)", usage="{room_code}", hidden=True)
    @check(roles=["modlead", "admin", "thmstaff"], dm_flag=False)
    async def new_room(self, ctx, room=""):
        if room == "":
            await ctx.send(s_room["no_code"])
        
        else:
            data = await api_fetch(c_api_url["room"].format(room))

            if data[room]["success"] == False:
                await ctx.send(s_room["code_not_found"].format(room))
                return

            channel = self.bot.get_channel(id_channel)

            await announce_room(channel, data, room)

    @commands.command(name="randomroom", description=s_room["randomroom_help_desc"])
    async def random_room(self, ctx):
        room = get_random_room()

        response = officialEmbed(room['title'], room['description'])
        response.set_thumbnail(url=room['image'])

        response.add_field(name="Room type", value=room['type'].capitalize(), inline=True)
        response.add_field(name="Difficulty", value=room['difficulty'].capitalize(), inline=True)
        response.add_field(name="Upvotes", value=room['upVotes'], inline=True)
        response.add_field(name="Sub required", value=bool_to_yesno(not room['freeToUse']), inline=True)
        response.add_field(name="Room creator", value=room['creator'], inline=True)

        response.url = f"{c_join_room}{room['code']}"

        await ctx.send(embed=response)

    async def new_room_listener(self):
        """Function responsible to loop and listen for a new room release."""

        # Setup the channel to send the announcements into.
        channel = self.bot.get_channel(id_channel)

        while True:
            # Reading the json and loading it.
            stored_data = None
            try:
                roomJson = open(c_room_data, "r").read()
                stored_data = json.loads(roomJson)
            except:
                with open(c_room_data, "w") as file:
                    stored_data = await api_fetch(c_api_url["newrooms"])
                    json.dump(stored_data, file)

            # Getting infos from the API.
            data = await api_fetch(c_api_url["newrooms"])

            # Getting the room codes from both JSONs.
            # Try-except to avoid wrongly parsed stuff [...] (making the bot more stable thx to this)
            try:
                new_room_code = data[0]["code"]
                last_room_code = stored_data["code"]
            except:
                copyfile(c_room_default_data, c_room_data)

                roomJson = open(c_room_data, "r").read()

                new_room_code = data[0]["code"]
                last_room_code = stored_data[0]["code"]

            # Check for new data.
            if new_room_code != last_room_code:
                await announce_room(channel, data[0])

            await asyncio.sleep(c_sleep_time)

    # Starts the auto listener to detect new rooms.
    @commands.Cog.listener()
    async def on_ready(self):
        await self.new_room_listener()


def setup(bot):
    bot.add_cog(Room(bot))
	
