import discord
from discord.ext import commands

import libs.config as config
from libs.embedmaker import officialEmbed

# QoL / TODO
# Look into integrating HelpJuice API so all topics can be retrieved via requests and parameters


###################
# Other variables #
###################

# Embeds data.
s_docs = config.get_string("docs")

# Retrieve list of all topics and commands & unexpected error message
s_topics = s_docs["topics"]
s_commands = s_docs["commands"]
s_error = s_docs["error"]



# Store all objects in strings "topics"
s_topics = s_docs["topics"] 

# THM Logo & Color for embed
c_docs_picture = config.get_config("info")["logo"]
c_docs_color = config.get_config("colors")["site"]


# Begin grabbing string entries for individual topics

# URL topic
s_url = s_docs["url"]
s_url_url = s_url["url"]
s_url_title = s_url["title"]
s_url_help = s_url["help_desc"]

# Verify topic
s_verify = s_docs["verify"]
s_verify_url = s_verify["url"]
s_verify_title = s_verify["title"]
s_verify_help = s_verify["help_desc"]

# Student topic
s_student = s_docs["student"]
s_student_url = s_student["url"]
s_student_title = s_student["title"]
s_student_help = s_student["help_desc"]

# Levels topic
s_levels = s_docs["levels"]
s_levels_url = s_levels["url"]
s_levels_title = s_levels["title"]
s_levels_help = s_levels["help_desc"]

# Room Notes topic
s_room_notes = s_docs["room_notes"]
s_room_notes_url = s_room_notes["url"]
s_room_notes_title = s_room_notes["title"]
s_room_notes_help = s_room_notes["help_desc"]

# Room Review topic
s_room_review = s_docs["room_review"]
s_room_review_url = s_room_review["url"]
s_room_review_title = s_room_review["title"]
s_room_review_help = s_room_review["help_desc"]

# Api topic
s_api = s_docs["api"]
s_api_url = s_api["url"]
s_api_title = s_api["title"]
s_api_help_desc = s_api["help_desc"]

# Koth topic
s_koth = s_docs["koth"]
s_koth_url = s_koth["url"]
s_koth_title = s_koth["title"]
s_koth_help_desc = s_koth["help_desc"]

# Free Path blog post
s_free_path = s_docs["free_path"]
s_free_path_url = s_free_path["url"]
s_free_path_title = s_free_path["title"]
s_free_path_help_desc = s_free_path["help_desc"]

# Free Path blog post
s_bug_bounty = s_docs["bug_bounty"]
s_bug_bounty_url = s_bug_bounty["url"]
s_bug_bounty_title = s_bug_bounty["title"]
s_bug_bounty_help_desc = s_bug_bounty["help_desc"]

#############
# Functions #
#############

# Make embeds.
def getEmbedDocs(n, v, t, c):
    """Setup embed for doc topics"""

    response = officialEmbed(n, v, color=c)
    response.set_thumbnail(url=t)
    return response

class Docs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="docs", description=s_docs["help_desc"], usage="[topic]", pass_context=True)
    async def docs(self, ctx, *, topic=""):
        if not topic:
            response = officialEmbed(title="Here are all of the possible topics!")
            response.set_thumbnail(url=(c_docs_picture))

            for i in range(1, len(s_commands)):
                response.add_field(name=s_commands[i], value=s_topics[i])

            await ctx.send(embed=response)
            return
        
        elif topic == "url":
            response = getEmbedDocs(s_url_title, s_url_url, c_docs_picture, c_docs_color)
            await ctx.send(embed=response)
        
        elif topic == "verify":
            response = getEmbedDocs(s_verify_title, s_verify_url, c_docs_picture, c_docs_color)
            await ctx.send(embed=response)
        
        elif topic == "student":
            response = getEmbedDocs(s_student_title, s_student_url, c_docs_picture, c_docs_color)
            await ctx.send(embed=response)


        elif topic == "levels":
            response = getEmbedDocs(s_levels_title, s_levels_url, c_docs_picture, c_docs_color)
            await ctx.send(embed=response)

        elif topic == "room-notes":
            response = getEmbedDocs(s_room_notes_title, s_room_notes_url, c_docs_picture, c_docs_color)
            await ctx.send(embed=response)

        elif topic == "room-review":
            response = getEmbedDocs(s_room_review_title, s_room_review_url, c_docs_picture, c_docs_color)
            await ctx.send(embed=response)

        elif topic == "api":
            response = getEmbedDocs(s_api_title, s_api_url, c_docs_picture, c_docs_color)
            await ctx.send(embed=response)
        
        elif topic == "koth":
            response = getEmbedDocs(s_koth_title, s_koth_url, c_docs_picture, c_docs_color)
            await ctx.send(embed=response)

        elif topic == "free-path":
            response = getEmbedDocs(s_free_path_title, s_free_path_url, c_docs_picture, c_docs_color)
            await ctx.send(embed=response)

        elif topic == "bug-bounty":
            response = getEmbedDocs(s_bug_bounty_title, s_bug_bounty_url, c_docs_picture, c_docs_color)
            await ctx.send(embed=response)

        # If anything other then the arguments are provided, say that the topic provided does not exist
        else:
            response = officialEmbed(title="That topic does not exist!")
            response.set_thumbnail(url=(c_docs_picture))

            await ctx.send(embed=response)
            return

def setup(bot):
    bot.add_cog(Docs(bot))
