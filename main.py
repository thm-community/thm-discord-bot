import discord
from discord.ext import commands
import time
import datetime
import json
import random


inputFile = "token.txt"
workingFile = open(inputFile)
token = workingFile.readline()

# Setting up the bot and prefix.
prefix = "!"
bot = commands.Bot(command_prefix=prefix)

# Saving the starting time.
start_time = time.time()

# Setting up extentions. (cogs)
extensions = ["cogs.room", "cogs.social", "cogs.rank","cogs.userrank","cogs.rolesync","cogs.rules","cogs.wiki","cogs.linkfetch", "cogs.fun", "cogs.devrole"]

# Quotes for the welcoming messages.
quotesF = json.loads(open("config/quotes.json", "r").read())
channelsF = json.loads(open("config/channels.json", "r").read())

specialQuotes = quotesF["specialQuotes"]
regularQuotes = quotesF["regularQuotes"]
welcomeChanID = channelsF["welcome"]

def getRegularQuote():
    return regularQuotes[random.randint(0, len(regularQuotes) - 1)]

def getSpecialQuote():
    return specialQuotes[random.randint(0, len(specialQuotes)-1)]

def isSpecialQuote():
    #About 10% chance to have a special quote.
    isSpecial = random.randint(0,100)
    return isSpecial <= 10

async def send_rules(member):
    response = discord.Embed(title="Rules", color=0xffff00)
    response.set_author(name="TryHackMe",icon_url="https://tryhackme.com/img/THMlogo.png")
    response.set_thumbnail(url="https://tryhackme.com/img/THMlogo.png")
    
    rulesF = json.loads(open("config/rules.json", "r").read())
    rules = rulesF["rules"]
    i = 0

    for rule in rules:
        response.add_field(name=(str(i+1) + "."), value=rule)
        i = i + 1

    response.set_footer(text="From the TryHackMe Official API!")
    
    channel = await member.create_dm()
    await channel.send(embed=response)

# Loading the cogs.
if __name__ == "__main__":
    print("Loading the COGS:")
    for extension in extensions:
        try:
            bot.load_extension(extension)
            print(f"\t{extension} loaded successfully.\n")
        except Exception as e:
            print(f"\tError occurred while loading {extension}")

# Logging the starting of the bot into the console.
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("DM me with !verify"))
    print("#- Logged in as {0.user}".format(bot)+"\n")


# Welcoming messages to new users.
@bot.event
async def on_member_join(member: discord.Member):
    channel = bot.get_channel(welcomeChanID)

    if isSpecialQuote():
        quip = getSpecialQuote()
        response = discord.Embed(title="Welcome!", description=quip, color=0xf5b400)
    else:
        quip = getRegularQuote()
        response = discord.Embed(title="Welcome!", description=quip, color=0xa20606)

    response.set_author(name="TryHackMe",icon_url="https://tryhackme.com/img/THMlogo.png")
    # The thumbnail here returns a 404 
    response.set_thumbnail(url="insert_thumbnail")
    response.add_field(name="Hey there!", value=member.mention + ", Welcome to the server!\nIf you need help with a room, ask in #rooms-help.\n\n You can also sync your THM rank on the discord! Use !verify in #bot-commands for more information!")
    
    if member not None:
        await send_rules(member)
        await channel.send(embed=response)


## Other commands.
# Uptime command.
@bot.command()
async def uptime(ctx):
    current_time = time.time()
    difference = int(round(current_time - start_time))
    text = str(datetime.timedelta(seconds=difference))
    
    embed = discord.Embed(colour=0x3289a8)
    embed.add_field(name="Uptime", value=text)
    embed.set_footer(text="TryHackMe")

    await ctx.channel.send(embed=embed)

# Ping command.
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")
    ping = await ctx.send("**__Calculating Elapsed Time__**")
    await ping.edit(content="**Calculated:\nPing rate:** {}ms".format(round(bot.latency, 3)))

# Starting the bot.
bot.run(token)
