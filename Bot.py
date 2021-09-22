import discord
from discord.ext import commands
import secret

bot = commands.Bot(command_prefix="!")

@bot.command()
async def MakeMeAChannel(ctx, inputMembers, channelName):
  print("Starting Channel Making")
  
  inputMembers = inputMembers.split(",")
  myMembers = []
  for member in ctx.guild.members:
    print(member.name)
    if member.name in inputMembers:
      myMembers.append(member)
  if len(myMembers) == 0:
    print("Couldn't find any Members")
  
  myChannel = await ctx.guild.create_voice_channel(channelName)

@bot.event
async def on_ready():
  print(f'{bot.user} has connected to Discord!')

@bot.listen()
async def on_message(message):
  if message.content[:13] == "Hey Mr. Hand!":
    await message.channel.send("Dont anger that which you don't understand")

bot.run(secret.token)