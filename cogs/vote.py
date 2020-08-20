import asyncio
import json
from datetime import datetime, timedelta

import discord
from discord.ext import commands

import libs.config as config
from libs.embedmaker import officialEmbed
from libs.utils import has_role


#####################
# Strings variables #
#####################

s_vote = config.get_string("vote")


###################
# Other variables #
###################

# Channel & role ID.
id_announcements = config.get_config("channels")["announcements"]
s_no_perm = config.get_string("commands")["no_perm"]
roles = config.get_config("roles")
id_admin = roles["admin"]
id_mod = roles["mod"]
# Persistence File.
file_persistence = config.get_config("persistence")["vote"]


#############
# Functions #
#############

def clear_file():
    """Clears the persistance file to default data. It returns the message ID if there is one."""

    ret = None

    file = open(file_persistence, "r").read()
    data = json.loads(file)

    if not "no_vote" in data:
        # Saves message ID.
        ret = data["message_id"]

    data = {"no_vote":True}
    with open(file_persistence, 'w') as outfile:
        json.dump(data, outfile)

    return ret


############
# COG Body #
############

class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def vote_output(self, data):
        """Send the output of the vote into the announcement channel."""

        deltaTime = datetime.strptime(data["ending_time"], "%Y-%m-%dT%H:%M:%S.%f") - datetime.now()
        vTimeSec = int(deltaTime.total_seconds())
        vDesc = data["desc"]
        vOpt = data["options"]
        vMessageId = data["message_id"]

        # Waits...
        # We check that the time is actually in the future.
        # Otherwise, send result now.
        if vTimeSec > 0:
            await asyncio.sleep(vTimeSec)

        # Sends results.
        try:
            announcementChan = self.bot.get_channel(id_announcements)
            vResult = (await announcementChan.fetch_message(vMessageId)).reactions

            embed = officialEmbed("Vote results", "Topic: " + vDesc)
            for i in range(0, len(vOpt)):
                embed.add_field(
                    name=vOpt[i], value=str(vResult[i].count-1))

            await announcementChan.send(embed=embed)
        except Exception as e:
            print(e)
        
        # Vote is finished, erase JSON data.
        clear_file()

    # Command to make a new vote.
    @commands.command(description=s_vote["help_desc"] + " (Admin)", hidden=True)
    async def vote(self, ctx):
        vDesc = ""
        vOpt = []
        vReac = []
        vTimeHour = 0

        # Remove the command.
        await ctx.message.delete()

        # Check for the user to be admin.
        if not has_role(ctx.author, id_admin):
            botMsg = await ctx.send(config.get_string("no_perm"))
            await asyncio.sleep(5)
            await botMsg.delete()
            return

        # Check for the author.
        def checkAuth(m):
            return m.author == ctx.author

        def checkDone(m):
            return (m.author == ctx.author and m.content.lower() == "done")

        botMsgCancel = await ctx.send(s_vote["cancel_message"])

        # Retrieve the vote's description.
        botMsg = await ctx.send(s_vote["vote_desc"])
        vDescMsg = await self.bot.wait_for('message', check=checkAuth)
        vDesc = vDescMsg.content

        await botMsg.delete()
        await vDescMsg.delete()

        if vDescMsg.content.lower() == "cancel":
            await botMsgCancel.delete()
            confirmDelMsg = await ctx.send(s_vote["canceled"])
            await asyncio.sleep(5)
            await confirmDelMsg.delete()
            return

        # Retrieve the vote's options and reactions.
        botMsg = await ctx.send(s_vote["vote_options"])

        isDone = False
        optMsg = []

        # Gettings all options.
        while not isDone:
            msg = await self.bot.wait_for('message', check=checkAuth)
            if msg.content.lower() == "done":
                isDone = True
            elif msg.content.lower() == "cancel":
                await botMsgCancel.delete()
                await botMsg.delete()
                await msg.delete()
                for m in optMsg:
                    await m.delete()

                confirmDelMsg = await ctx.send(s_vote["canceled"])
                await asyncio.sleep(5)
                await confirmDelMsg.delete()
                return
            else:
                vOpt.append(msg.content)
            optMsg.append(msg)

        # Clearing the messages.
        await botMsg.delete()
        for m in optMsg:
            await m.delete()

        # Doing the same but for reactions.
        botMsgText = s_vote["vote_reactions"]
        for i in range(0, len(vOpt)):
            botMsgText += ("\n" + str(i+1) + ". - " + vOpt[i])
        botMsg = await ctx.send(botMsgText)

        # Waits for the DONE message.
        isDone = False
        while not isDone:
            msg = await self.bot.wait_for('message', check=checkAuth)

            if msg.content.lower() == "cancel":
                await botMsgCancel.delete()
                await botMsg.delete()
                await msg.delete()
                confirmDelMsg = await ctx.send(s_vote["canceled"])
                await asyncio.sleep(5)
                await confirmDelMsg.delete()
                return

            # Checks if the amount of emojis matches the amount of options.
            cacheBotMsg = await ctx.channel.fetch_message(botMsg.id)

            if len(cacheBotMsg.reactions) != len(vOpt):
                await msg.delete()
                errorMsg = await ctx.send(s_vote["reactions_amount_wrong"])
                await asyncio.sleep(5)
                await errorMsg.delete()
            else:
                isDone = True

        # Sets the emojis.
        for r in cacheBotMsg.reactions:
            vReac.append(r.emoji)

        # Clears msg.
        await botMsg.delete()
        await msg.delete()

        # Gets the time the vote should last.
        isDone = False
        while(not isDone):
            timeAsk = await ctx.send(s_vote["vote_time"])
            msg = await self.bot.wait_for('message', check=checkAuth)

            if msg.content.lower() == "cancel":
                await botMsgCancel.delete()
                await msg.delete()
                await timeAsk.delete()
                confirmDelMsg = await ctx.send(s_vote["canceled"])
                await asyncio.sleep(5)
                await confirmDelMsg.delete()
                return

            try:
                vTimeHour = int(msg.content)
                isDone = True
            except:
                errorMsg = await ctx.send(s_vote["time_int_only"])
                await asyncio.sleep(2)
                await errorMsg.delete()
                isDone = False
            finally:
                await timeAsk.delete()
        await msg.delete()

        # Confirmation embed.
        embed = officialEmbed(title=s_vote["recap"], desc=vDesc, footer=s_vote["recap_time"].format(vTimeHour))
        for i in range(0, len(vOpt)):
            embed.add_field(name=vReac[i], value=vOpt[i])

        # Sends embed.
        botEmbed = await ctx.send(embed=embed)

        # Asks for validation.
        botMsg = await ctx.send(s_vote["confirm"])
        voteValid = await self.bot.wait_for('message', check=checkAuth)

        # Checks validation's answer.
        if not voteValid.content.lower() == "yes":
            cancelMsg = await ctx.send(s_vote["canceled"])

            # Removes useless msg.
            await botMsgCancel.delete()
            await botEmbed.delete()
            await botMsg.delete()
            await voteValid.delete()
            await cancelMsg.delete()
        else:
            # Removes useless msg.
            await botMsgCancel.delete()
            await botMsg.delete()
            await voteValid.delete()

            # Makes embed.
            embed = officialEmbed("Vote", vDesc)
            for i in range(0, len(vOpt)):
                embed.add_field(name=vReac[i], value=vOpt[i])

            # Sends the vote.
            chan_announcement = self.bot.get_channel(id_announcements)
            vEmbed = await chan_announcement.send(embed=embed)
            # Adds the reactions to it.
            for i in range(0, len(vReac)):
                await vEmbed.add_reaction(vReac[i])

            # Saves it in the persistence file.
            endingTime = (datetime.now() + timedelta(hours=vTimeHour)).strftime('%Y-%m-%dT%H:%M:%S.%f')
            data = {"desc": vDesc, "options":vOpt, "ending_time":endingTime, "message_id":vEmbed.id}

            with open(file_persistence, 'w') as outfile:
                json.dump(data, outfile)

            # Waits and fetches results.
            await self.vote_output(data)

    # Command to stop ongoing vote.
    @commands.command(description=s_vote["help_desc_canceled"] + " (Admin)", hidden=True)
    async def votecancel(self, ctx):
        if has_role(ctx.author, id_admin):
            vote_id = clear_file()

            if vote_id != None:
                chan_announcement = self.bot.get_channel(id_announcements)
                vote_msg = (await chan_announcement.fetch_message(vote_id))
                await vote_msg.delete()
                
                await ctx.send(s_vote["canceled"])
            else:
                await ctx.send(s_vote["nothing_to_cancel"])

    # Loads persistence, and checks if a vote is ongoing.
    @commands.Cog.listener()
    async def on_ready(self):
        # Loads.
        try:
            file = open(file_persistence, "r").read()
            data = json.loads(file)
        except:
            data = {"no_vote":True}
            with open(file_persistence, 'w') as file_out:
                json.dump(data, file_out)

        # Check if there is an ongoing vote.
        if not "no_vote" in data:
            print("[INFO]\tVote found!")
            # Gets back to the vote.
            await self.vote_output(data)

def setup(bot):
    bot.add_cog(Vote(bot))
