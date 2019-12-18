from discord.ext import commands
from requests.auth import HTTPBasicAuth
import discord 
import requests
import json
import time

# Role IDs.
rolesF = json.loads(open("config/roles.json", "r").read())
adminID = rolesF["admin"]

# Issue's data.
creds = [cred.replace("\n","") for cred in open("jira_creds.txt","r")]
auth = HTTPBasicAuth(creds[0], creds[1])

issueName = "no_title"                      # The issue's title.
issueDesc = "no_description"                # The issue's desc.
issueProject = "BUG"                        # The issue's project.
issueType = "10021"                         # The issue's type. (10004 is task)
baseUrl = "https://tryhackme.atlassian.net" # The base URL.
issueUrl = baseUrl + "/rest/api/3/issue"    # The REST API url.

# The headers of the request.
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def hasRole(member, id):
        for role in member.roles:
                if id == role.id:
                        return True
        return False


class Jira(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    

    # Command to make a new issue to JIRA.
    @commands.command()
    async def issue(self,ctx):

        # Remove the command.
        await ctx.message.delete()

        # Check for the user to be admin.
        if not hasRole(ctx.author, adminID):
            botMsg = await ctx.send("You do not have the permission to do that.")
            time.sleep(5)
            await botMsg.delete()
            return

        # Check for the author.
        def check(m):
            return m.author == ctx.author 

        # Retrieve the issue's name.
        botMsg = await ctx.send("Please provide a name for the new issue:")
        issueNameMsg = await self.bot.wait_for('message', check=check)
        issueName = issueNameMsg.content

        await botMsg.delete()
        await issueNameMsg.delete()


        # Retrieve the issue's desc.
        botMsg = await ctx.send("Now please provide a description:")

        issueDescMsg = await self.bot.wait_for('message', check=check)
        issueDesc = issueDescMsg.content + "\n -- Created by: " + ctx.author.display_name

        await botMsg.delete()
        await issueDescMsg.delete()

        # Confirmation embed.
        embed = discord.Embed(title="New issue", description="This is the input you are about to create:")
        embed.set_author(name="TryHackMe",icon_url="http://tryhackme.com/img/THMlogo.png")
        embed.add_field(name="Name", value=issueName)
        embed.add_field(name="Description", value=issueDesc)
        embed.set_footer(text="From the TryHackMe Official API!")

        # Sends embed.
        botEmbed = await ctx.send(embed=embed)
        
        # Asks for validation.
        botMsg = await ctx.send("To confirm enter ***yes*** or anything else to cancel. (not case sensitive)")
        issueValid = await self.bot.wait_for('message', check=check)

        # Checks validation's answer.
        if issueValid.content.lower() == "yes":
            # Removes useless msg.
            await botMsg.delete()
            await issueValid.delete()

            # Creates the issue on JIRA.
            ## The payload made out of the issue's vars.
            payload = json.dumps( {
                "fields": {
                    "summary": issueName,
                    "issuetype": {
                        "id": issueType
                    },
                    "project": {
                        "key": issueProject
                    },
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                "text": issueDesc,
                                "type": "text"
                                }
                            ]
                            }
                        ]
                    }
                }
            } )

            ## Sends the the POST request.
            response = requests.request(
                "POST",
                issueUrl,
                data=payload,
                headers=headers,
                auth=auth
            )
            print("### JIRA issue creation report:")
            print(issueName + " : " + issueDesc)
            print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
            
            # Notifies the user.
            await ctx.send("Issue has been **created** by " + ctx.author.mention +  "!")
        else:
            # Removes useless msg.
            await botEmbed.delete()
            await botMsg.delete()
            await issueValid.delete()

            # Removes cancel msg.
            botMsg = await ctx.send("You have **cancelled** the issue!")
            time.sleep(5)
            await botMsg.delete()


def setup(bot):
    bot.add_cog(Jira(bot))
