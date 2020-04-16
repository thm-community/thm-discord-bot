import discord
from PIL import Image, ImageOps, ImageDraw, ImageFont
import requests
import io
from io import BytesIO
import json
from discord.ext import commands

import random

# Fonts and color.
font1 = ImageFont.truetype("fonts/Ubuntu-Light.ttf", 75)
font2 = ImageFont.truetype("fonts/Ubuntu-Light.ttf", 50)
font3 = ImageFont.truetype("fonts/Ubuntu-Bold.ttf", 30)
red = (162,6,6)
gray = (52,60,66)
green = (136,204,20)
white = (255, 255, 255)

apiURL = "https://tryhackme.com/api/leaderboards"
pages = {1:5,2:10,3:15,4:20,5:25,6:30,7:35,8:40,9:45,10:50}

def getUsernames(page, style):

    pages = {1:5,2:10,3:15,4:20,5:25,6:30,7:35,8:40,9:45,10:50}
    response = requests.get("https://tryhackme.com/api/leaderboards")
    data = response.text
    data = json.loads(data)[style]
    num = pages[page]-5
    r_num = num+1
    usernames = []
    for e,i in enumerate(data[num:pages[page]]):
        usernames.append(i["username"])
    return usernames

def getAvatars(page, style):

    pages = {1:5,2:10,3:15,4:20,5:25,6:30,7:35,8:40,9:45,10:50}
    response = requests.get("https://tryhackme.com/api/leaderboards")
    data = response.text
    data = json.loads(data)[style]
    num = pages[page]-5
    r_num = num+1
    avatars = []
    for e,i in enumerate(data[num:pages[page]]):
        avatars.append(i["avatar"])
    return avatars

def getPoints(page, style):

    pages = {1:5,2:10,3:15,4:20,5:25,6:30,7:35,8:40,9:45,10:50}
    response = requests.get("https://tryhackme.com/api/leaderboards")
    data = response.text
    data = json.loads(data)[style]
    num = pages[page]-5
    r_num = num+1
    points = []
    pointsType = 0
    if style == "topUsersMonthly":
        pointsType = "monthlyPoints"
    else:
        pointsType = "points"
    for e,i in enumerate(data[num:pages[page]]):
        points.append(i[pointsType])
    return points

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
class Rank(commands.Cog,name="Leaderboard Commands"):
        def __init__(self,bot):
                self.bot = bot

        @commands.command(description="Prints the leaderboard.")
        async def leaderboard(self,ctx,*,page: int=1):
		#Starts typing indicator
		async with ctx.channel.typing():
			#image_gen(page)
			#Logs and prints starting message
			print("Generating leaderboard...")
			message = await ctx.send("Generating leaderboard...")

			# Adds a white flag reaction to the user's command.
			#emoji = "\N{Waving White Flag}"
			#await ctx.message.add_reaction(emoji)

			# New image.
			img = Image.new('RGB', (1000, 1000), color=gray)

			# Adding logo.
			logo = Image.open("images/THMlogo.png")
			logo.thumbnail((logo.size[0]/4, logo.size[1]/4), Image.ANTIALIAS)
			img.paste(logo, (775, 15), logo)
			d = ImageDraw.Draw(img)

			# Adding texts. (leaderboard, mady with, invite link..)
			d.text((12, 20), "Leaderboard:", font=font1, fill=white)
			d.text((865-len(str(page))*25, 920), "Page {}".format(page), font=font2, fill=white)
			d.text((12, 925), "Made with love by the TryHackMe Discord Bot", font=font3, fill=white)
			d.text((12, 955), "discord.gg/GzVZtGX", font=font3, fill=white)

			# Masking for the users.
			size = (128, 128)
			mask = Image.new("L", size, 0)
			mask_draw = ImageDraw.Draw(mask)
			mask_draw.ellipse((0, 0) + size, fill=255)

			# Retrieving the users, points and avatar.
			avatars = getAvatars(page, "topUsers")
			usernames = getUsernames(page, "topUsers")
			points = getPoints(page, "topUsers")

			base = 150
			index = 0
			pos = (8, base)
			edge = 975

			#Adding each user.
			for x in usernames:
				response = requests.get(avatars[index])

				# Saving temp image, then adding it to the rest.
				temp_img = Image.open(BytesIO(response.content))
				temp_img.save('images/temp{}.png'.format(index))
				output = ImageOps.fit(temp_img, mask.size, centering=(0.5, 0.5))
				img.paste(output, (83, base), mask)

				# Adding the texts.
				d.text((222, base+32), "{}".format(usernames[index]), font=font2, fill=white)
				d.text((8, base+32), "{}.".format(index+1+(page-1)*5), font=font2, fill=white)

				d.text((970-(len(str(points[index]))*25), base+32), str(points[index]), font=font2, fill=green)
				base += 160
				pos = (8, base)
				index += 1

			# Finalizing, and sending.
			large_img = img.resize((img.size[0]*4, img.size[1]*4))
			large_img.save('images/leaderboard_output.png')
			
			#Edits starting message with the file
			await message.edit(content=None,file=discord.File('images/leaderboard_output.png'))
            

        @commands.command(description="Prints this month's leaderboard.")
        async def monthly(self,ctx,*,page: int=1):
		#Starts typing indicator
		async with ctx.channel.typing():

			#image_gen(page)
			#Logs and prints starting message
			print("Generating leaderboard...")
			message = await ctx.send("Generating leaderboard...")
			

			# Adds a white flag reaction to the user's command.
			#emoji = "\N{Waving White Flag}"
			#await ctx.message.add_reaction(emoji)

			# New image.
			img = Image.new('RGB', (1000, 1000), color=gray)

			# Adding logo.
			logo = Image.open("images/THMlogo.png")
			logo.thumbnail((logo.size[0]/4, logo.size[1]/4), Image.ANTIALIAS)
			img.paste(logo, (775, 15), logo)
			d = ImageDraw.Draw(img)

			# Adding texts. (leaderboard, mady with, invite link..)
			d.text((12, 20), "Monthly Leaderboard:", font=font1, fill=white)
			d.text((865-len(str(page))*25, 920), "Page {}".format(page), font=font2, fill=white)
			d.text((12, 925), "Made with love by the TryHackMe Discord Bot", font=font3, fill=white)
			d.text((12, 955), "discord.gg/GzVZtGX", font=font3, fill=white)

			# Masking for the users.
			size = (128, 128)
			mask = Image.new("L", size, 0)
			mask_draw = ImageDraw.Draw(mask)
			mask_draw.ellipse((0, 0) + size, fill=255)

			# Retrieving the users, points and avatar.
			avatars = getAvatars(page, "topUsersMonthly")
			usernames = getUsernames(page, "topUsersMonthly")
			points = getPoints(page, "topUsersMonthly")

			base = 150
			index = 0
			pos = (8, base)
			edge = 975

			#Adding each user.
			for x in usernames:
				response = requests.get(avatars[index])

				# Saving temp image, then adding it to the rest.
				temp_img = Image.open(BytesIO(response.content))
				temp_img.save('images/temp{}.png'.format(index))
				output = ImageOps.fit(temp_img, mask.size, centering=(0.5, 0.5))
				img.paste(output, (83, base), mask)

				# Adding the texts.
				d.text((222, base+32), "{}".format(usernames[index]), font=font2, fill=white)
				d.text((8, base+32), "{}.".format(index+1+(page-1)*5), font=font2, fill=white)

				d.text((970-(len(str(points[index]))*25), base+32), str(points[index]), font=font2, fill=green)
				base += 160
				pos = (8, base)
				index += 1

			# Finalizing, and sending.
			large_img = img.resize((img.size[0]*4, img.size[1]*4))
			large_img.save('images/leaderboard_output.png')
			
			#Edits starting message with the file
			await message.edit(content=None, file=discord.File('images/leaderboard_output.png'))
            

def setup(bot):
	bot.add_cog(Rank(bot))
				

        
