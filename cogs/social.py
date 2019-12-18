from discord.ext import commands
import discord, random, time, asyncio, requests, json,tweepy
    
# Twitter API key.
credsFile = "twitter_creds.txt"

# Embeds data.
## URLs.
gitURL = "https://github.com/DarkStar7471/THM-Bot"
twitterURL = "https://twitter.com/realtryhackme"
redditURL = "https://www.reddit.com/r/tryhackme/"
websiteURL = "https://tryhackme.com/"

## Titles.
gitTitle = "Bot's Github Repository Link"
twitterTitle = "TryHackMe's Twitter Account:"
redditTitle = "TryHackMe's Subreddit:"
websiteTitle = "TryHackMe:"

## Pictures.
gitPic = "https://raw.githubusercontent.com/DarkStar7471/THM-Bot/master/images/computer.png"
twitterPic = "https://i.imgur.com/rImenvh.png"
redditPic = "https://i.imgur.com/rgK8YTD.png"
websitePic = "https://tryhackme.com/img/THMlogo.png"

## Colors
twitterColor = 0x08a0e9
redditColor = 0xff5700
websiteColor = 0x000000
gitColor = 0x0463C4

# Make embeds.
def getEmbedSocial(n, v, t, c):
    response = discord.Embed(color=c)
    response.set_author(name="TryHackMe",icon_url=websitePic)
    response.set_thumbnail(url=t)
    response.add_field(name=n, value=v)
    return response

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def github(self, ctx):
        response = getEmbedSocial(gitTitle, gitURL, gitPic, gitColor)
        await ctx.send(embed=response)
    @commands.command()
    async def twitter(self, ctx):
        response = getEmbedSocial(twitterTitle, twitterURL, twitterPic, twitterColor)
        await ctx.send(embed=response)

    @commands.command()
    async def reddit(self, ctx):
        response = getEmbedSocial(redditTitle, redditURL, redditPic, redditColor)
        await ctx.send(embed=response)

    @commands.command()
    async def website(self, ctx):
        response = getEmbedSocial(websiteTitle, websiteURL, websitePic, websiteColor)
        await ctx.send(embed=response)

    @commands.command()
    async def social(self, ctx):
        response = getEmbedSocial(twitterTitle, twitterURL, twitterPic, twitterColor)
        await ctx.send(embed=response)

        response = getEmbedSocial(redditTitle, redditURL, redditPic, redditColor)
        await ctx.send(embed=response)

        response = getEmbedSocial(websiteTitle, websiteURL, websitePic, websiteColor)
        await ctx.send(embed=response)
    
    @commands.command()
    async def tweet(self,ctx):
        # Secret twitter API key.
        creds = [cred.replace("\n","") for cred in open(credsFile,"r")]

        # Auth & get.
        auth = tweepy.OAuthHandler(creds[0], creds[1])
        auth.set_access_token(creds[2], creds[3])
        api = tweepy.API(auth)
        tryhackme_tweets = api.user_timeline(screen_name = 'RealTryHackMe', count = 20, include_rts = False)

        # Sends first found tweet. (and not reply.)
        for tweet in tryhackme_tweets:
            if not tweet.in_reply_to_screen_name:
                await ctx.send("https://twitter.com/RealTryHackMe/status/" + str(tweet.id))
                break

def setup(bot):
    bot.add_cog(Social(bot))
