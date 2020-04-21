import discord
from PIL import Image, ImageOps, ImageDraw, ImageFont
import requests
from io import BytesIO
from discord.ext import commands

import libs.thm_api as thm

# Fonts and color.
font1 = ImageFont.truetype("fonts/Ubuntu-Light.ttf", 75)
font2 = ImageFont.truetype("fonts/Ubuntu-Light.ttf", 50)
font3 = ImageFont.truetype("fonts/Ubuntu-Bold.ttf", 30)
red = (162, 6, 6)
gray = (52, 60, 66)
green = (136, 204, 20)
white = (255, 255, 255)

'''
def image_gen(page):
        img = Image.new('RGB', (1000, 1000), color=gray)
        logo = Image.open("THMlogo.png")
        logo.thumbnail((logo.size[0]/4, logo.size[1]/4), Image.ANTIALIAS)
        img.paste(logo, (775, 15), logo)
        d = ImageDraw.Draw(img)
        d.text((12, 20), "Leaderboard:", font=font1, fill=white)
        d.text((865-len(str(page))*25, 920), "Page {}".format(page), font=font2, fill=white)
        d.text((12, 925), "Made with love by the TryHackMe Discord Bot", font=font3, fill=white)
        d.text((12, 955), "discord.gg/GzVZtGX", font=font3, fill=white)
        size = (128, 128)
        mask = Image.new("L", size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0) + size, fill=255)
        avatars = getAvatars(page)
        usernames = getUsernames(page)
        points = getPoints(page)
        base = 150
        index = 0
        pos = (8, base)
        edge = 975
        for x in usernames:
                response = requests.get(avatars[index])
                temp_img = Image.open(BytesIO(response.content))
                temp_img.save('temp{}.png'.format(index))
                output = ImageOps.fit(temp_img, mask.size, centering=(0.5, 0.5))
                img.paste(output, (83, base), mask)
                d.text((222, base+32), "{}".format(usernames[index]), font=font2, fill=white)
                d.text((8, base+32), "{}.".format(index+1+(page-1)*5), font=font2, fill=white)

                d.text((970-(len(str(points[index]))*25), base+32), str(points[index]), font=font2, fill=green)
                base += 160
                pos = (8, base)
                index += 1


        large_img = img.resize((img.size[0]*4, img.size[1]*4))
        large_img.save('images/image.png')
'''


class Rank(commands.Cog, name="Leaderboard Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Prints the leaderboard.")
    async def leaderboard(self, ctx, *, page: int = 1):
        # image_gen(page)
        print("Generating leaderboard...\n")

        # Adds a white flag reaction to the user's command.
        emoji = "\N{Waving White Flag}"
        await ctx.message.add_reaction(emoji)

        # New image.
        img = Image.new('RGB', (1000, 1000), color=gray)

        # Adding logo.
        logo = Image.open("images/THMlogo.png")
        logo.thumbnail((logo.size[0] / 4, logo.size[1] / 4), Image.ANTIALIAS)
        img.paste(logo, (775, 15), logo)
        d = ImageDraw.Draw(img)

        # Adding texts. (leaderboard, mady with, invite link..)
        d.text((12, 20), "Leaderboard:", font=font1, fill=white)
        d.text((865 - len(str(page)) * 25, 920), "Page {}".format(page), font=font2, fill=white)
        d.text((12, 925), "Made with love by the TryHackMe Discord Bot", font=font3, fill=white)
        d.text((12, 955), "discord.gg/GzVZtGX", font=font3, fill=white)

        # Masking for the users.
        size = (128, 128)
        mask = Image.new("L", size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0) + size, fill=255)

        # Retrieving the users, points and avatar.
        users = thm.getLeaderboard(page, False)

        base = 150
        index = 0

        # Adding each user.
        for user in users:
            res = requests.get(user['avatar'])

            # Saving temp image, then adding it to the rest.
            temp_img = Image.open(BytesIO(res.content))
            temp_img.save('images/temp{}.png'.format(index))
            output = ImageOps.fit(temp_img, mask.size, centering=(0.5, 0.5))
            img.paste(output, (83, base), mask)

            # Adding the texts.
            d.text((222, base + 32), "{}".format(user['username']), font=font2, fill=white)
            d.text((8, base + 32), "{}.".format(index + 1 + (page - 1) * 5), font=font2, fill=white)

            d.text((970 - (len(str(user['points'])) * 25), base + 32), str(user['points']), font=font2, fill=green)
            base += 160
            index += 1

        # Finalizing, and sending.
        large_img = img.resize((img.size[0] * 4, img.size[1] * 4))
        large_img.save('images/leaderboard_output.png')
        await ctx.send(file=discord.File('images/leaderboard_output.png'))

    @commands.command(description="Prints this month's leaderboard.")
    async def monthly(self, ctx, *, page: int = 1):
        # image_gen(page)
        print("Generating leaderboard...\n")

        # Adds a white flag reaction to the user's command.
        emoji = "\N{Waving White Flag}"
        await ctx.message.add_reaction(emoji)

        # New image.
        img = Image.new('RGB', (1000, 1000), color=gray)

        # Adding logo.
        logo = Image.open("images/THMlogo.png")
        logo.thumbnail((logo.size[0] / 4, logo.size[1] / 4), Image.ANTIALIAS)
        img.paste(logo, (775, 15), logo)
        d = ImageDraw.Draw(img)

        # Adding texts. (leaderboard, mady with, invite link..)
        d.text((12, 20), "Monthly Leaderboard:", font=font1, fill=white)
        d.text((865 - len(str(page)) * 25, 920), "Page {}".format(page), font=font2, fill=white)
        d.text((12, 925), "Made with love by the TryHackMe Discord Bot", font=font3, fill=white)
        d.text((12, 955), "discord.gg/GzVZtGX", font=font3, fill=white)

        # Masking for the users.
        size = (128, 128)
        mask = Image.new("L", size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0) + size, fill=255)

        # Retrieving the users, points and avatar.
        users = thm.getLeaderboard(page, True)

        base = 150
        index = 0

        # Adding each user.
        for user in users:
            res = requests.get(user['avatar'])

            # Saving temp image, then adding it to the rest.
            temp_img = Image.open(BytesIO(res.content))
            temp_img.save('images/temp{}.png'.format(index))
            output = ImageOps.fit(temp_img, mask.size, centering=(0.5, 0.5))
            img.paste(output, (83, base), mask)

            # Adding the texts.
            d.text((222, base + 32), "{}".format(user['username']), font=font2, fill=white)
            d.text((8, base + 32), "{}.".format(index + 1 + (page - 1) * 5), font=font2, fill=white)

            d.text((970 - (len(str(user['monthlyPoints'])) * 25), base + 32), str(user['monthlyPoints']), font=font2,
                   fill=green)
            base += 160
            index += 1

        # Finalizing, and sending.
        large_img = img.resize((img.size[0] * 4, img.size[1] * 4))
        large_img.save('images/leaderboard_output.png')
        await ctx.send(file=discord.File('images/leaderboard_output.png'))


def setup(bot):
    bot.add_cog(Rank(bot))
