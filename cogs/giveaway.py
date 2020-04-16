from discord.ext import commands
import discord 
import json, asyncio, random

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

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    

    # Command to make a new giveaway.
    @commands.command(description="Create a giveaway.", hidden=True)
    async def giveaway(self,ctx):

        gDesc = ""
        gReac = None
        gTimeHour = 0

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
        
        botMsgCancel = await ctx.send("Enter CANCEL at anytime to cancel the giveaway.")

        # Retrieve the giveaway's description.
        botMsg = await ctx.send("Please provide a description for the giveaway:")
        gDescMsg = await self.bot.wait_for('message', check=checkAuth)
        gDesc = gDescMsg.content

        await botMsg.delete()
        await gDescMsg.delete()

        if gDescMsg.content.lower() == "cancel":
            await botMsgCancel.delete()
            confirmDelMsg = await ctx.send("Giveaway canceled.")
            await asyncio.sleep(5)
            await confirmDelMsg.delete()
            return

        # Getting the reaction to enter the giveaway.
        botMsgText = "Now please react to this message with the reaction users should use to enter giveaway. Then send DONE."
        botMsg = await ctx.send(botMsgText)
        
        # Waits for the reaction and DONE message.
        isDone = False
        while not isDone:
            msg = await self.bot.wait_for('message', check=checkAuth)
            
            if msg.content.lower() == "cancel":
                await botMsgCancel.delete()
                await botMsg.delete()
                await msg.delete()
                confirmDelMsg = await ctx.send("Giveaway canceled.")
                await asyncio.sleep(5)
                await confirmDelMsg.delete()
                return
            
            # Checks if the amount of emojis matches the amount of options.
            ## We need to re-cache the message to retrieve the reactions.
            cacheBotMsg = await ctx.channel.fetch_message(botMsg.id)
            
            if len(cacheBotMsg.reactions) != 1:
                await msg.delete()
                errorMsg = await ctx.send("Only one reaction allowed, please fix it and send DONE.")
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
            timeAsk = await ctx.send("Time the giveaway should last in hours:")
            msg = await self.bot.wait_for('message', check=checkAuth)

            if msg.content.lower() == "cancel":
                await botMsgCancel.delete()
                await msg.delete()
                await timeAsk.delete()
                confirmDelMsg = await ctx.send("Giveaway canceled.")
                await asyncio.sleep(5)
                await confirmDelMsg.delete()
                return
            
            try:
                gTimeHour = int(msg.content)
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
        embed = officialEmbed("This is the giveaway you are about to create:", gDesc,footer="Lasting for "+str(gTimeHour)+" hour(s).")
        embed.add_field(name="Enter-giveaway reaction", value=gReac)

        # Sends embed.
        botEmbed = await ctx.send(embed=embed)
        
        # Asks for validation.
        botMsg = await ctx.send("To confirm enter ***yes*** or anything else to cancel. (not case sensitive)")
        giveawayValid = await self.bot.wait_for('message', check=checkAuth)

        # Checks validation's answer.
        if not giveawayValid.content.lower() == "yes":
            cancelMsg = await ctx.send("You canceled the giveaway.")
            
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
            embed.add_field(name="Enter-giveaway reaction", value=gReac)

            # Sends the giveaway.
            announcementChan = self.bot.get_channel(channelID)
            gEmbed = await announcementChan.send(embed=embed)
            # Adds the reactions to it.
            await gEmbed.add_reaction(gReac)

            # Waits...
            await asyncio.sleep(15)
            #time.sleep(gTimeHour*60*60)

            # Sends results.
            # try:
            gResult = (await announcementChan.fetch_message(gEmbed.id)).reactions[0]

            embed = officialEmbed("Giveaway results", gDesc)

            # Retrives the winner, excluding the BOT.
            winner = None
            users = await gResult.users().flatten()

            while winner == None or winner.id == self.bot.user.id:
                winner = random.choice(users)

            embed.add_field(name="Winner is", value=winner.mention+", congratulations!")

            await announcementChan.send(embed=embed)
            # except:
            #     print("Giveaway has been deleted.")

def setup(bot):
    bot.add_cog(Giveaway(bot))
