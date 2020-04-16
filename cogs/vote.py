from discord.ext import commands
import discord 
import json
import asyncio

from libs.embedmaker import officialEmbed

# Channel ID.
channelJson = open("config/channels.json", "r").read()
channelID = json.loads(channelJson)["announcements"]

# Role IDs.
rolesF = json.loads(open("config/roles.json", "r").read())
adminID = rolesF["admin"]

def hasRole(member, id):
        for role in member.roles:
                if id == role.id:
                        return True
        return False

class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    

    # Command to make a new vote.
    @commands.command(description="Create a vote.", hidden=True)
    async def vote(self,ctx):

        vDesc = ""
        vOpt = []
        vReac = []
        vTimeHour = 0

        # Remove the command.
        await ctx.message.delete()

        # Check for the user to be admin.
        if not hasRole(ctx.author, adminID):
            botMsg = await ctx.send("You do not have the permission to do that.")
            await asyncio.sleep(5)
            await botMsg.delete()
            return

        # Check for the author.
        def checkAuth(m):
            return m.author == ctx.author 

        def checkDone(m):
            return (m.author == ctx.author and m.content.lower() == "done")
        
        botMsgCancel = await ctx.send("Enter CANCEL at anytime to cancel the vote.")

        # Retrieve the vote's description.
        botMsg = await ctx.send("Please provide a description for the vote:")
        vDescMsg = await self.bot.wait_for('message', check=checkAuth)
        vDesc = vDescMsg.content

        await botMsg.delete()
        await vDescMsg.delete()

        if vDescMsg.content.lower() == "cancel":
            await botMsgCancel.delete()
            confirmDelMsg = await ctx.send("Vote canceled.")
            await asyncio.sleep(5)
            await confirmDelMsg.delete()
            return

        # Retrieve the vote's options and reactions.
        botMsg = await ctx.send("Now please send a message for each options; send DONE (not case sensitive) when you are done.")

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

                confirmDelMsg = await ctx.send("Vote canceled.")
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
        botMsgText = "Now please react to this message with the respective emote of each option; then send DONE:"
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
                confirmDelMsg = await ctx.send("Vote canceled.")
                await asyncio.sleep(5)
                await confirmDelMsg.delete()
                return

            # Checks if the amount of emojis matches the amount of options.
            cacheBotMsg = await ctx.channel.fetch_message(botMsg.id)

            if len(cacheBotMsg.reactions) != len(vOpt):
                await msg.delete()
                errorMsg = await ctx.send("Wrong amount of reactions, please fix it and send DONE.")
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
            timeAsk = await ctx.send("Time the vote should last in hours:")
            msg = await self.bot.wait_for('message', check=checkAuth)

            if msg.content.lower() == "cancel":
                await botMsgCancel.delete()
                await msg.delete()
                await timeAsk.delete()
                confirmDelMsg = await ctx.send("Vote canceled.")
                await asyncio.sleep(5)
                await confirmDelMsg.delete()
                return
            
            try:
                vTimeHour = int(msg.content)
                isDone = True
            except:
                errorMsg = await ctx.send("Numbers only, please retry.")
                await asyncio.sleep(2)
                await errorMsg.delete()
                isDone = False
            finally:
                await timeAsk.delete()
        await msg.delete()
        
        # Confirmation embed.
        embed = officialEmbed("This is the vote you are about to create:", "Lasting for "+str(vTimeHour)+" hour(s).")
        for i in range(0, len(vOpt)):
            embed.add_field(name=vReac[i], value=vOpt[i])

        # Sends embed.
        botEmbed = await ctx.send(embed=embed)
        
        # Asks for validation.
        botMsg = await ctx.send("To confirm enter ***yes*** or anything else to cancel. (not case sensitive)")
        voteValid = await self.bot.wait_for('message', check=checkAuth)

        # Checks validation's answer.
        if not voteValid.content.lower() == "yes":
            cancelMsg = await ctx.send("You canceled the vote.")
            
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
            announcementChann = self.bot.get_channel(channelID)
            vEmbed = await announcementChann.send(embed=embed)
            # Adds the reactions to it.
            for i in range(0, len(vReac)):
                await vEmbed.add_reaction(vReac[i])

            # Waits...
            #time.sleep(15)
            await asyncio.sleep(vTimeHour*60*60)

            # Sends results.
            try:
                vResult = (await announcementChann.fetch_message(vEmbed.id)).reactions

                embed = officialEmbed("Vote results", "Topic: "+vDesc)
                for i in range(0, len(vOpt)):
                    embed.add_field(name=vOpt[i], value=str(vResult[i].count-1))

                await announcementChann.send(embed=embed)
            except:
                print("Vote has been deleted.")

def setup(bot):
    bot.add_cog(Vote(bot))
