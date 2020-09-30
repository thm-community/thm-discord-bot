"""Leaderboard Cog
Allows users to view the top and monthly leaderboards on the discord.

User Usage:
leaderboard [page]
monthly [page]

Other Functionality:
- retrieves leaderboard data from THM and outputs into 
  the announcements every month (disabled)
"""

import asyncio
import datetime
import typing
import io
import json
import random
from io import BytesIO
from math import ceil

import discord
import requests
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageOps

import libs.config as config
from libs.thm_api import get_leaderboard_data


####################
# Config variables #
####################

c_monthly_data = config.get_config("data_files")["monthly_leaderboard"]
c_channels = config.get_config("channels")


#####################
# Strings variables #
#####################

s_leader = config.get_string("ranks")["leaderboard"]
s_monthly = config.get_string("ranks")["monthly"]


###################
# Other variables #
###################

# Channels ID.
id_announcement = c_channels["announcements"]

# Fonts and color.
font1 = ImageFont.truetype("fonts/Ubuntu-Light.ttf", 75)
font2 = ImageFont.truetype("fonts/Ubuntu-Light.ttf", 50)
font3 = ImageFont.truetype("fonts/Ubuntu-Bold.ttf", 30)
red = (162, 6, 6)
gray = (52, 60, 66)
green = (136, 204, 20)
white = (255, 255, 255)


############
# COG Body #
############

class Leaderboard(commands.Cog, name="Leaderboard Commands"):
    def __init__(self, bot):
        self.bot = bot

    async def generate_leaderboard(self, channel, page: int = 1, monthly: bool = False, country: str = None):
        """Generates and sends a leaderboard image based on the parameters"""

        # Getting the leaderboard data (in future will also handle other args like countries)
        leaderboard_data = get_leaderboard_data(monthly=monthly, country=country)
        available_pages = ceil(len(leaderboard_data) / 5)

        # Page count check
        if available_pages == 0:
            return await channel.send(s_leader['invalid_country'])
        elif page > available_pages or page < 1:
            return await channel.send(s_leader['invalid_page'].format(available_pages))

        # Extracting specific users
        data = leaderboard_data[(page * 5) - 5:(page * 5)]

        if monthly:
            print(s_monthly['generating'])
        else:
            print(s_leader['generating'])

        # New image.
        img = Image.new('RGB', (1000, 1000), color=gray)

        # Adding logo.
        logo = Image.open("images/THMlogo.png")
        logo.thumbnail((logo.size[0] / 4, logo.size[1] / 4), Image.ANTIALIAS)
        img.paste(logo, (775, 15), logo)
        d = ImageDraw.Draw(img)

        # Adding texts. (leaderboard, mady with, invite link..)
        if monthly:
            d.text((12, 20), "Monthly Leaderboard:", font=font1, fill=white)
        else:
            d.text((12, 20), "Leaderboard:", font=font1, fill=white)

        d.text((865 - len(str(page)) * 25, 920),
               "Page {}".format(page), font=font2, fill=white)
        d.text((12, 925), s_leader["footer"],
               font=font3, fill=white)
        d.text((12, 955), config.get_config("url")["invite"], font=font3, fill=white)

        # Masking for the users.
        size = (128, 128)
        mask = Image.new("L", size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0) + size, fill=255)

        base = 150
        index = 0

        # Adding each user.
        for user in data:
            response = requests.get(user['avatar'])

            # Saving temp image, then adding it to the rest.
            temp_img = Image.open(BytesIO(response.content))
            temp_img.save('images/temp{}.png'.format(index))
            output = ImageOps.fit(temp_img, mask.size, centering=(0.5, 0.5))
            img.paste(output, (83, base), mask)

            # Adding the texts.
            d.text((222, base + 32),
                   "{}".format(user['username']), font=font2, fill=white)
            d.text((8, base + 32), "{}.".format(index + 1 +
                                                (page - 1) * 5), font=font2, fill=white)

            if monthly:
                d.text((970 - (len(str(user['monthlyPoints'])) * 25), base + 32),
                       str(user['monthlyPoints']), font=font2, fill=green)
            else:
                d.text((970 - (len(str(user['points'])) * 25), base + 32),
                       str(user['points']), font=font2, fill=green)
            base += 160
            index += 1

        # Finalizing, and sending.
        large_img = img.resize((img.size[0] * 4, img.size[1] * 4))
        large_img.save('images/leaderboard_output.png')
        await channel.send(file=discord.File('images/leaderboard_output.png'))

    async def monthly_announcement(self):
        """Sends the monthly leaderboard in the announcement channel."""

        date = datetime.datetime.today()
        month = date.month
        
        # If file doesn't exists, creates it with current month.
        try:
            file = open(c_monthly_data, "r+")
            data = file.read()
        except:
            file = open(c_monthly_data, "w")
            data = month
            file.write(str(data))

        file.close()

        if int(data) != month:
            channel = self.chan_announcement

            await self.monthly_leaderboard(channel)
            file = open(c_monthly_data, "w")
            file.write(str(month))
            file.close()

        await asyncio.sleep(config.get_config("sleep_time")["monthly_leaderboard"])

    @commands.command(description=s_leader["help_desc"], usage="[page] / [country [page]]")
    async def leaderboard(self, ctx, *args):
        page = 1
        country = None

        if len(args) > 0:
            try:
                page = int(args[0])
            except:
                country = args[0]
        if len(args) > 1:
            try:
                page = int(args[1])
            except:
                pass

        # The bot will appear as typing while executing the command.
        async with ctx.channel.typing():
            await self.generate_leaderboard(ctx.channel, page, monthly=False, country=country)

    @commands.command(description=s_monthly["help_desc"], usage="[page] / [country [page]]")
    async def monthly(self, ctx, *args):
        page = 1
        country = None

        if len(args) > 0:
            try:
                page = int(args[0])
            except:
                country = args[0]
        if len(args) > 1:
            try:
                page = int(args[1])
            except:
                pass

        # The bot will appear as typing while executing the command.
        async with ctx.channel.typing():
            await self.generate_leaderboard(ctx.channel, page, monthly=True, country=country)

    # Starts the monthly leaderboard announcement.
    @commands.Cog.listener()
    async def on_ready(self):
        self.chan_announcement = self.bot.get_channel(id_announcement)
        await self.monthly_announcement()


def setup(bot):
    bot.add_cog(Leaderboard(bot))
