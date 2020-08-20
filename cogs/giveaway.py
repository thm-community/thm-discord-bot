import asyncio
import json
import random
from datetime import datetime, timedelta

import discord
from discord.ext import commands

import libs.config as config
from libs.embedmaker import officialEmbed
from libs.utils import has_role


####################
# Config variables #
####################

# Channel and role ID.
id_announcements = config.get_config("channels")["announcements"]
roles = config.get_config("roles")
id_admin = roles["admin"]
id_mod = roles["mod"]
s_no_perm = config.get_string("commands")["no_perm"]
# Persistence File.
file_persistence = config.get_config("persistence")["giveaway"]

# Strings.
s_no_perm = config.get_string("commands")["no_perm"]
s_giveaway = config.get_string("giveaway")


#############
# Functions #
#############

def clear_file():
    """Resets the giveaway persistance file to an empty one."""

    ret = None
    
    file = open(file_persistence, "r").read()
    data = json.loads(file)

    # If there is existing data.
    if not "no_giveaway" in data:
        # Saves message ID.
        ret = data["message_id"]

    # Resets the data.
    data = {"no_giveaway":True}

    # Saves data in file.
    with open(file_persistence, 'w') as file_out:
        json.dump(data, file_out)

    return ret


############
# COG Body #
############

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def giveaway_output(self, data):
        """Handle the end of a giveaway given its data. (Announces winner, reset persistance, etc)"""

        deltaTime = datetime.strptime(data["ending_time"], "%Y-%m-%dT%H:%M:%S.%f") - datetime.now()
        gTimeSec = int(deltaTime.total_seconds())

        gDesc = data["desc"]
        gMessageId = data["message_id"]

        # Waits...
        # We check that the time is actually in the future.
        if gTimeSec > 0:
            await asyncio.sleep(gTimeSec)

        # Sends results.
        try:
            gResult = (await self.chan_announcement.fetch_message(gMessageId)).reactions[0]

            embed = officialEmbed("Giveaway results", gDesc)

            # Retrives the winner, excluding the BOT.
            winner = None
            users = await gResult.users().flatten()

            while winner == None or winner.id == self.bot.user.id:
                winner = random.choice(users)

            embed.add_field(name=s_giveaway["announce_field_title"],
                            value=s_giveaway["announce_field_value"].format(winner.mention))

            await self.chan_announcement.send(embed=embed)
        except:
            print(s_giveaway["canceled"])

        # Giveaway is finished, erase JSON data.
        clear_file()

    # Command to make a new giveaway.
    @commands.command(description=s_giveaway["help_desc"] + " (Admin)", hidden=True)
    async def giveaway(self, ctx):

        gDesc = ""
        gReac = None
        gTimeHour = 0

        # Remove the command.
        await ctx.message.delete()

        # Check for the user to be admin.
        if not has_role(ctx.author, id_admin):
            botMsg = await ctx.send(s_no_perm)
            await asyncio.sleep(5)
            await botMsg.delete()
            return

        # Check for the author.
        def checkAuth(m):
            return m.author == ctx.author

        def checkDone(m):
            return (m.author == ctx.author and m.content.lower() == s_giveaway["confirm_word"])

        botMsgCancel = await ctx.send(s_giveaway["cancel"])

        # Retrieve the giveaway's description.
        botMsg = await ctx.send(s_giveaway["desc"])
        gDescMsg = await self.bot.wait_for('message', check=checkAuth)
        gDesc = gDescMsg.content

        await botMsg.delete()
        await gDescMsg.delete()

        if gDescMsg.content.lower() == s_giveaway["cancel_word"]:
            await botMsgCancel.delete()
            confirmDelMsg = await ctx.send(s_giveaway["canceled"])
            await asyncio.sleep(5)
            await confirmDelMsg.delete()
            return

        # Getting the reaction to enter the giveaway.
        botMsgText = s_giveaway["reaction"]
        botMsg = await ctx.send(botMsgText)

        # Waits for the reaction and DONE message.
        isDone = False
        while not isDone:
            msg = await self.bot.wait_for('message', check=checkAuth)

            if msg.content.lower() == s_giveaway["cancel"]:
                await botMsgCancel.delete()
                await botMsg.delete()
                await msg.delete()
                confirmDelMsg = await ctx.send(s_giveaway["canceled"])
                await asyncio.sleep(5)
                await confirmDelMsg.delete()
                return

            # Checks if the amount of emojis matches the amount of options.
            # We need to re-cache the message to retrieve the reactions.
            cacheBotMsg = await ctx.channel.fetch_message(botMsg.id)

            if len(cacheBotMsg.reactions) != 1:
                await msg.delete()
                errorMsg = await ctx.send(s_giveaway["reaction_limit"])
                await asyncio.sleep(5)
                await errorMsg.delete()
            else:
                isDone = True
                reaction = cacheBotMsg.reactions[0]

        # Asigns reaction.
        gReac = reaction.emoji

        # Clears msg.
        await botMsg.delete()
        await msg.delete()

        # Gets the time the giveaway should last.
        isDone = False
        while(not isDone):
            timeAsk = await ctx.send(s_giveaway["time"])
            msg = await self.bot.wait_for('message', check=checkAuth)

            if msg.content.lower() == s_giveaway["cancel_word"]:
                await botMsgCancel.delete()
                await msg.delete()
                await timeAsk.delete()

                confirmDelMsg = await ctx.send(s_giveaway["canceled"])
                await asyncio.sleep(5)
                await confirmDelMsg.delete()
                return

            try:
                gTimeHour = int(msg.content)
                isDone = True
            except:
                errorMsg = await ctx.send(s_giveaway["time_int_only"])
                await asyncio.sleep(2)
                await errorMsg.delete()

                isDone = False
            finally:
                await timeAsk.delete()
        await msg.delete()

        # Confirmation embed.
        embed = officialEmbed(s_giveaway["confirm_title"],
                              gDesc, footer=s_giveaway["confirm_footer"].format(gTimeHour))
        embed.add_field(name=s_giveaway["confirm_reaction"], value=gReac)

        # Sends embed.
        botEmbed = await ctx.send(embed=embed)

        # Asks for validation.
        botMsg = await ctx.send(s_giveaway["confirm_text"])
        giveawayValid = await self.bot.wait_for('message', check=checkAuth)

        # Checks validation's answer.
        if not giveawayValid.content.lower() == "yes":
            cancelMsg = await ctx.send(s_giveaway["canceled"])

            # Removes useless msg.
            await botMsgCancel.delete()
            await botEmbed.delete()
            await botMsg.delete()
            await giveawayValid.delete()
            await cancelMsg.delete()
        else:
            # Removes useless msg.
            await botMsgCancel.delete()
            await botMsg.delete()
            await giveawayValid.delete()

            # Makes embed.
            embed = officialEmbed("Giveaway", gDesc)
            embed.add_field(name=s_giveaway["announce_reaction"], value=gReac)

            # Sends the giveaway.
            chan_announcement = self.bot.get_channel(id_announcements)
            gEmbed = await chan_announcement.send(embed=embed)

            # Adds the reactions to it.
            await gEmbed.add_reaction(gReac)

            # Saves it in the persistence file.
            endingTime = (datetime.now() + timedelta(hours=gTimeHour)).strftime('%Y-%m-%dT%H:%M:%S.%f')
            data = {"desc": gDesc, "ending_time":endingTime, "message_id":gEmbed.id}

            with open(file_persistence, 'w') as outfile:
                json.dump(data, outfile)

            # Waits and fetches results.
            await self.giveaway_output(data)

    # Command to stop ongoing giveaway.
    @commands.command(name="giveawaycancel", description=s_giveaway["help_desc_canceled"] + " (Admin)", hidden=True)
    async def giveaway_cancel(self, ctx):
        if has_role(ctx.author, id_admin):
            giveaway_id = clear_file()

            if giveaway_id != None:
                chan_announcement = self.bot.get_channel(id_announcements)
                giveaway_msg = (await chan_announcement.fetch_message(giveaway_id))
                await giveaway_msg.delete()

                await ctx.send(s_giveaway["canceled"])
            else:
                await ctx.send(s_giveaway["nothing_to_cancel"])

    # Loads persistence, and checks if a giveaway is ongoing.
    @commands.Cog.listener()
    async def on_ready(self):
        # Loads.
        try:
            file = open(file_persistence, "r").read()
            data = json.loads(file)
        except:
            data = {"no_giveaway":True}
            with open(file_persistence, 'w') as file_out:
                json.dump(data, file_out)

        # Check if there is an ongoing giveaway.
        if not "no_giveaway" in data:
            print("[INFO]\tGiveaway found!")

            # Goes back to where it stopped.
            await self.giveaway_output(data)

def setup(bot):
    bot.add_cog(Giveaway(bot))
