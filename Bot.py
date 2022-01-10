import discord, datetime, asyncio, os, random, time
from discord.ext import commands

try:  
  os.environ["DISCORD_BOT_TOKEN"]
except KeyError: 
  print("Please set the environment variable DISCORD_BOT_TOKEN")
  exit(1)

secret_token = (os.environ["DISCORD_BOT_TOKEN"])

UsersLists = {}
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", case_insensitive=True) #intents=intents,)

@bot.slash_command(guild_ids=[882043693274628167])
async def showmylist(ctx):
  print(f"Started a ShowMyList Command at {datetime.datetime.now()}")
  if ctx.channel.type != 'private' and ctx.author.name != 'TPBubbleU':
    warningMessage = await ctx.send("Don't message here! It's not private")
    await asyncio.sleep(5)
    await warningMessage.delete()
    await ctx.message.delete()
    return
  if ctx.author.id in UsersLists.keys():
    await ctx.send(str(UsersLists[ctx.author.id]))
  else:
    await ctx.send("No List found for you")

@bot.slash_command(guild_ids=[882043693274628167])
async def addtomylist(ctx, *inputmembers):
  print(f"Started a AddtoMyList Command at {datetime.datetime.now()}")
  if ctx.channel.type != 'private' and ctx.author.name != 'TPBubbleU':
    warningMessage = await ctx.send("Don't message here! It's not private")
    await asyncio.sleep(5)
    await warningMessage.delete()
    await ctx.message.delete()
    return
  UsersLists[ctx.author.id] = list(map(str.strip, " ".join(list(inputmembers)).split(",")))
  await ctx.send("Updated")

@bot.event
async def on_ready():
  print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_voice_state_update(member, before, after):
  print(f"Started a on_voice_state_update at {datetime.datetime.now()}")
  if member.bot: #Quick and easy out if the event is caused by a bot
    return
  SpecialChannelName = 'Round Up A Posse'
  # Make a new channel if the user joins the special channel
  if after is not None and after.channel is not None and after.channel.name == SpecialChannelName:
    print(f"Started the process of making a new channel at {datetime.datetime.now()}")
    guild = after.channel.guild
    
    overwrites = None
    if member.id in UsersLists.keys(): 
      guildMembers = await guild.fetch_members().flatten()
      overwriteMemberList = []
      for i in guildMembers:
        for j in UsersLists[member.id]:
          if j == i.nick or j == i.name:
            print("Adding " + (i.nick if i.nick else i.name) + " to the list")
            overwriteMemberList.append(i)
      # Lets go out and actually make the overwrites object
      overwrites = {
        guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=False),
        # This is the "Townspeople" role
        guild.get_role(891126367498928148): discord.PermissionOverwrite(connect=False, view_channel=False),
        member: discord.PermissionOverwrite(connect=True, view_channel=True)
      }
      for i in overwriteMemberList:
        overwrites[i] = discord.PermissionOverwrite(connect=True, view_channel=True)
    categoryChannel = guild.get_channel(887583365442715708)
    newChannel = await guild.create_voice_channel(name=(member.nick if member.nick else member.name), bitrate=128000, 
                                                  category=categoryChannel, overwrites=overwrites)
    await member.move_to(channel=newChannel)
  # Delete voice channels if no one is in them after state updates and they are not the Special name
  if after is not None and after.channel is not None:
    if len(after.channel.voice_states) == 0 and after.channel.name != SpecialChannelName:
      print(f"Started the process of deleting a channel at {datetime.datetime.now()}")
      await after.channel.delete()
  if before is not None and before.channel is not None:
    if len(before.channel.voice_states) == 0 and before.channel.name != SpecialChannelName:
      print(f"Started the process of deleting a channel at {datetime.datetime.now()}")
      await before.channel.delete()
      
  # Lets have a random chance to make a sound on entry
  if random.random() <= .1 and after is not None and after.channel.name != SpecialChannelName: #10% chance
    print(f"Started the process of making random noise at {datetime.datetime.now()}")
    for i in bot.voice_clients:
      await i.disconnect(force=True)
    vc = await after.channel.connect()
    vc.play(discord.FFmpegPCMAudio('TheGoodtheBadandtheUgly.mp3',options='-filter:a "volume=0.4"'))
    time.sleep(5)
    await vc.disconnect(force=True)
  print(f"Ended a on_voice_state_update at {datetime.datetime.now()}")

@bot.listen()
async def on_message(message):
  if message.content[:13] == "Hey Mr. Hand!":
    await message.channel.send("Dont anger that which you don't understand")
  if message.channel.name == "post-office" and datetime.datetime.now().weekday() == 6:
    await message.channel.send("https://tenor.com/view/no-post-on-sunday-vernon-dursley-sundays-harry-potter-gif-10875689")

bot.run(secret_token)
