#### Tek Oot Discord bot ####
### By: Iwan ###
#Invite link: https://discord.com/api/oauth2/authorize?client_id=742278272515178547&permissions=8&scope=bot

##IMPORTS##
import discord
from discord.ext import commands
import asyncio
import sys
import random
import time
import configparser
import os
import sqlite3



##VARIABLES##
global VERSION
VERSION = '0.1a'

global DEBUG
DEBUG = True

global botID
botID = 742278272515178547

global guildID
guildID = 741935998648451113

#Currently Unused
global logChannel
logChannel = 742290977581957182

#Lists
userCommands = ["help", "test", "roll", "flip", "remind", "addquote", "quote", "pfp", "info", "version", "changelog"]



##OBJECTS##
bot = commands.Bot(command_prefix="!")

connection = sqlite3.connect('OtterBrain.db')
cur = connection.cursor()



##UTILS##

#Remove default help command
bot.remove_command('help')

def getTokens():
	config = configparser.ConfigParser()
	if not os.path.isfile("tokens.cfg"):
		print("tokens file missing. ")
		print("Creating one now.")
		config.add_section("Tokens")
		config.set("Tokens", "Bot", "null")
		with open ('tokens.cfg', 'w') as configfile:
			config.write(configfile)
		print("File created.")
		print("Please edit tokens.cfg and then restart.")
		_ = input()
	else:
		config.read('tokens.cfg')
		return config.get('Tokens', 'Bot')

def debug(msg):
	if DEBUG == True:
		print("DEBUG: " + msg)

def create_tables():
	cur.execute('''CREATE TABLE IF NOT EXISTS quoteList
                     (QUOTES TEXT)''')

def register_quote(usr, quote):
	quote = usr.name + ': "' + quote + '"'
	cur.execute("INSERT INTO quoteList (quotes) VALUES (?)", (quote,))
	connection.commit()
    
def load_quotes():
	print("Loading Quotes...")
	cur.execute('''SELECT * FROM quoteList''')
	global quotes
	quotes = cur.fetchall()

def get_quote():
	quote = random.choice(quotes)
	quote = str(quote)
	quote = quote.strip("('',)")
	return quote
    
def get_changelog(ver):
	with open ('changelogs/' + ver + '.txt', 'r') as changelog:
		changelog = changelog.read()
		changelog = changelog.splitlines()
	changelog = str(changelog)
	changelog = changelog.replace("',", "\n")
	changelog = changelog.split("['],")
	return changelog



##Bot Events##
@bot.event
async def on_ready():
	print("Discord.py version: " + discord.__version__)
	print("Logged in as: " + bot.user.name)
	print("ID: " + str(bot.user.id))
	print("------------------")
	_activity = discord.Game("with other cute Oots")
	await bot.change_presence(activity=_activity)



##USER COMMANDS##

#New Help command
@bot.command(pass_context = True)
async def help(ctx):
	usrCmds = '\n'.join("!" + str(c) for c in userCommands)
	em = discord.Embed(title='', description=usrCmds, colour=0xFF0000)
	em.set_author(name='Commands:', icon_url=bot.user.avatar_url)
	await ctx.message.channel.send(embed=em)

#Retrieve current version
@bot.command()
async def version(ctx):
	await ctx.channel.send("I am currently on version " + VERSION)
    
#View Changelog
@bot.command(pass_context = True)
async def changelog(ctx, ver: str=VERSION):
	await ctx.channel.send("Changelog for version " + ver + ":")
	for x in get_changelog(ver):
		await ctx.channel.send("`" + str(x).strip("['],").replace("'", "") + "`")

#Dice roll
@bot.command()
async def roll(ctx, *, dice : str=None):
	if dice == None:
		await ctx.channel.send('Format has to be in NdN!')
		return
	try:
		rolls, limit = map(int, dice.split('d'))
	except Exception:
		await ctx.channel.send('Format has to be in NdN!')
		return

#Flip a coin
@bot.command(pass_context = True)
async def flip(ctx):
	await ctx.channel.send("Okay, I'll flip it!")
	await asyncio.sleep(3)
	if random.choice([True, False]) == True:
		await ctx.channel.send(ctx.message.author.mention + ": the result is.......**HEADS**!")
	else:
		await ctx.channel.send(ctx.message.author.mention + ": the result is.......**TAILS**!")

#Remind-Me command
@bot.group(pass_context = True)
async def remind(ctx, time: str = "0", *, reminder: str="null"):
	time = int(time)
	if time == 0 or reminder == "null":
		await ctx.channel.send("Correct Usage: !remind <time in minutes> <reminder>")
		await ctx.channel.send("Example: !remind 5 Tell me how reminders work")
		return
	else:
		await ctx.message.delete()
		await ctx.channel.send("Okay, " + ctx.message.author.mention + "! I'll remind you :smile:")
		await asyncio.sleep(time * 60)
		await ctx.message.author.send("You wanted me to remind you: " + reminder)

#Command for ADDING quotes
@bot.command(pass_context = True)
async def addquote(ctx, member: discord.Member = None, *, quote: str=None):
	if member == None or quote == None:
		await ctx.channel.send("You must mention a user and add a quote!")
		await ctx.channel.send("Example: `!addquote @Iwan I love quotes`")
	elif member.id == botID:
		await ctx.channel.send("ERROR: UNAUTHORIZED! You are not allowed to quote me. Muahahaha!")
		return
	else:
		register_quote(member, quote)
		await ctx.message.delete()
		await ctx.channel.send("Quote added :thumbsup:")
		load_quotes()

#Retrieve quote
@bot.command()
async def quote(ctx):
	await ctx.channel.send(get_quote())

#Get User's profile pic (will return command-sender's pic if no user is specified)
@bot.command(pass_context = True)
async def pfp(ctx, member: discord.Member=None):
	if member==None:
		member = ctx.message.author
	await ctx.channel.send(ctx.author.mention + ": Here you go!\n" + str(member.avatar_url_as(static_format="png", size=1024)))

#Retrieves information on a user. (user will be command-sender if no user is specified)
@bot.command(pass_context = True)
async def info(ctx, member: discord.Member=None):
	if member == None:
		member = ctx.message.author
	info = "Joined guild on: " + member.joined_at.strftime("%A %B %d, %Y at %I:%M%p") + "\n"
	info = info + "Account created on: " + member.created_at.strftime("%A %B %d, %Y at %I:%M%p")
	em = discord.Embed(title='', description=info, colour=0xFF0000)
	em.set_author(name=member.name, icon_url=member.avatar_url)
	await ctx.channel.send(embed=em)




###Runtime, baby! Let's go!###
print ('Getting ready...')
print('Loading TekOot v' + VERSION)
create_tables()
load_quotes()
bot.run(getTokens())