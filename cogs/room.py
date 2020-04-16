from discord.ext import commands
import discord, random, asyncio, aiohttp, json
import ast

from libs.embedmaker import officialEmbed

# Channel ID.
channelJson = open("config/channels.json", "r").read()
channelID = json.loads(channelJson)["announcements"]

# Role IDs.
rolesF = json.loads(open("config/roles.json", "r").read())
adminID = rolesF["admin"]

# API
api_url = "https://tryhackme.com/api/"


# Role managment function.
def hasRole(member, id):
        for role in member.roles:
                if id == role.id:
                        return True
        return False

# Sending announcement function.
async def send(channel, json_data, code=None):
    # Set up embed.
    img = json_data["image"]
    title = json_data["title"]
    if code==None:
        code = "http://tryhackme.com/room/" + str(json_data["code"])
    else:
        code = "http://tryhackme.com/room/" + code
    description = json_data["description"]

    embed = officialEmbed(title, description)
    embed.set_image(url=img)

    # Send messages.
    await channel.send("A new room is available!  |  Check it out: "+code, embed=embed)

    # Updates local file.
    with open("config/room.json", "w") as file:
        json.dump(json_data, file)

class Room(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Learn how to use OpenVPN to connect to the network.")
    async def vpn(self, ctx):
        response = officialEmbed()
        response.set_thumbnail(url="https://tryhackme.com/room/openvpn")
        response.add_field(name="Learn how to use OpenVPN to connect to our network!", value="https://tryhackme.com/room/openvpn")
        await ctx.send(embed=response)

    @commands.command(description="Learn how to look for duplicate instance of your OpenVPN connection.")
    async def multivpn(self, ctx):
        response = officialEmbed()
        response.set_thumbnail(url="https://tryhackme.com/room/openvpn")
        response.add_field(name="• Step 1", value="Type ps aux | grep openvpn into your terminal and press enter")
        response.add_field(name="• Step 2", value="If there's more than one line (and the second doesn't have \"grep\" in it), do the following steps")
        response.add_field(name="• Step 3", value="Type killall openvpn into your terminal and press enter")
        response.add_field(name="• Step 4", value="Start the VPN with sudo openvpn <path-to-config>")
        await ctx.send(embed=response)

    @commands.command(description="Get the writeups for a room.", usage="{room_code}")
    async def writeup(self, ctx, room_code):
        # Request to the API.
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url+"room/"+room_code) as new_data:
                text = await new_data.read()
                json_data = json.loads(text)

                # If the specified code is wrong.
                if json_data["success"] == False:
                    botMsg = await ctx.send("Sorry, but the room code ``"+room_code+"`` could not be found.")

                    await asyncio.sleep(5)
                    await botMsg.delete()
                    await ctx.message.delete()

                    return

                # If there is no writeup.
                if len(json_data["writeups"]) == 0:
                    await ctx.send("Sorry, there is no writeup for this room.")
                    return

                # Set up embed.
                img = json_data["image"]
                title = json_data["title"]
                link = "http://tryhackme.com/room/" + room_code

                embed = officialEmbed(title, link)
                embed.set_image(url=img)

                for wu in json_data["writeups"]:
                    embed.add_field(name="By: "+wu["username"], value=wu["link"])

                # Send messages.
                await ctx.send(embed=embed)     

    @commands.command(description="Manually announce the last room.", hidden=True)
    async def room(self, ctx):
        if not hasRole(ctx.author, adminID):
            botMsg = await ctx.send("You do not have the permission to do that.")
            
            await asyncio.sleep(5)

            await botMsg.delete()
            await ctx.message.delete()
            return
        
        # Gets channel.
        channel = self.bot.get_channel(channelID)

        # Getting the API's JSON.
        async with aiohttp.ClientSession() as session:
            async with session.get("http://tryhackme.com/api/newrooms") as new_data:
                text = await new_data.read()
                json_data = json.loads(text) 
        
        await send(channel, json_data[0])

    @commands.command(name="newroom", description="Manually announce a new room.", usage="{room_code}", hidden=True)
    async def new_room(self, ctx, room):
        if not hasRole(ctx.author, adminID):
            botMsg = await ctx.send("You do not have the permission to do that.")
            
            await asyncio.sleep(5)

            await botMsg.delete()
            await ctx.message.delete()
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url+"room/"+room) as new_data:
                text = await new_data.read()
                json_data = json.loads(text)

                if json_data["success"] == False:
                    await ctx.send("Sorry, but the room code ``"+room+"`` could not be found.")
                    return

                channelJson = open("config/channels.json", "r").read()
                channelID = json.loads(channelJson)["announcements"]
                channel = self.bot.get_channel(channelID)

                await send(channel, json_data, room)

    async def new_room_listener(self):
        # Setup the channel to send the announcements into.
        channelJson = open("config/channels.json", "r").read()
        channelID = json.loads(channelJson)["announcements"]
        channel = self.bot.get_channel(channelID)
        
        while True:
          
            # Reading the json and loading it.
            roomJson = open("config/room.json", "r").read()
            stored_data = json.loads(roomJson)

            # Getting infos from the API.
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url+"newrooms") as new_data:

                    text = await new_data.read()
                    json_data = json.loads(text)

                    # Getting the titles from both JSONs.
                    # Try-except to avoid wrongly [...] (making the bot more stable thx to this)
                    try:
                        titleJsonData = json_data[0]["title"]
                        titleStoredData = stored_data["title"]
                    except:
                        copyfile("config/room_default.json", "config/room.json")
                        
                        roomJson = open("config/room.json", "r").read()

                        titleJsonData = json_data[0]["title"]
                        titleStoredData = stored_data[0]["title"]


                    # Check for new data.
                    if titleJsonData != titleStoredData:
                        await send(channel, json_data[0])
                            
            await asyncio.sleep(60)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.new_room_listener()


def setup(bot):
    bot.add_cog(Room(bot))
