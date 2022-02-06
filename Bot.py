import discord, datetime, asyncio, os, random, time
from discord.ext import commands
from discord.ui import Button, View
from Games.LoveLetter import LLGame

try:  
  os.environ["DISCORD_BOT_TOKEN"]
except KeyError: 
  print("Please set the environment variable DISCORD_BOT_TOKEN")
  exit(1)

secret_token = (os.environ["DISCORD_BOT_TOKEN"])

UsersLists = {}
intents = discord.Intents.default()
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", case_insensitive=True, intents=intents)
servers = [882043693274628167]

###############################
## Town things (Horsey Game) ##
###############################

# @bot.slash_command(guild_ids=servers, name="guide-me-through-town", description="Have the hand guide you through town")
# async def guidethroughtown(ctx):
#   print(f"Started a GuideThroughTown Command at {datetime.datetime.now()}")
#   townView = View()
#   async def corral_Button_Callback(interaction):
#     corralView = View()
    
  
#   townView.add_item(Button(label="Go to the Corral", style=discord.ButtonStyle.green))
#   townView.add_item(Button(label="Go to the Saloon", style=discord.ButtonStyle.green))
#   townView.add_item(Button(label="Go to the Stables", style=discord.ButtonStyle.green))
#   townView.add_item(Button(label="Go to the General Store", style=discord.ButtonStyle.green))
#   await ctx.respond("Welcome to the Town", view=townView, ephemeral=True)
  
##################################
## Secret Discord Voices Things ##
##################################

def getUserData(id):
  if id not in UsersLists.keys():
    UsersLists[id] = {"PosseList":[],"PosseName":None}
  return UsersLists[id]

@bot.slash_command(guild_ids=servers, name="rename-posse", description="Change the name of the voice channel when you round up a posse")
async def renameposse(ctx, posse_name: discord.Option(str, required=True)):
  print(f"Started a RenamePosse Command at {datetime.datetime.now()}")
  userData = getUserData(ctx.author.id)
  UsersLists[ctx.author.id]['PosseName'] = posse_name
  await ctx.respond(content=f"Posse name updated to {posse_name}", ephemeral=True)

@bot.slash_command(guild_ids=servers, name="who-is-in-my-posse", description="Show who will be allowed in voice when you round up a posse")
async def showmylist(ctx):
  print(f"Started a ShowMyList Command at {datetime.datetime.now()}")
  userData = getUserData(ctx.author.id)
  if userData['PosseList']:
    responseContent = ', '.join([str(bot.get_user(i)) for i in userData['PosseList']]) + " are currently in your posse" 
    await ctx.respond(content=responseContent, ephemeral=True)
  else:
    await ctx.respond(content="No posse list found for you", ephemeral=True)

@bot.slash_command(guild_ids=servers, name="add-to-my-posse", description="Add user(s) allowed in voice when you round up a posse")
async def addtomylist(ctx, member1: discord.Option(discord.Member, required=True), 
                           member2: discord.Option(discord.Member, required=False), 
                           member3: discord.Option(discord.Member, required=False)):
  print(f"Started a AddtoMyList Command at {datetime.datetime.now()}")
  userData = getUserData(ctx.author.id)
  # Append the authors list with an id if the member exists
  for i in [member1, member2, member3]:
    if i: 
      UsersLists[ctx.author.id]['PosseList'].append(i.id)
  # Respond to the user to let them know it worked
  await ctx.respond(content="Added " + ", ".join([str(i) for i in [member1,member2,member3] if i]) + " to the posse", ephemeral=True)

@bot.slash_command(guild_ids=servers, name="remove-from-my-posse", description="Remove user(s) allowed in voice when you round up a posse")
async def removefrommylist(ctx, member1: discord.Option(discord.Member, required=True), 
                                member2: discord.Option(discord.Member, required=False), 
                                member3: discord.Option(discord.Member, required=False)):
  print(f"Started a RemoveFromMyList Command at {datetime.datetime.now()}")
  userData = getUserData(ctx.author.id)
  # Append the authors list with an id if the member exists
  for i in [member1, member2, member3]:
    if i and i.id in UsersLists[ctx.author.id]['PosseList']:
      UsersLists[ctx.author.id]['PosseList'].remove(i.id)
  # Respond to the user to let them know it worked
  await ctx.respond(content="Removed " + ", ".join([str(i) for i in [member1,member2,member3] if i]) + " from the posse", ephemeral=True)

###############################
## New Discord Voices Things ##
###############################
  
@bot.event
async def on_voice_state_update(member, before, after):
  #print(f"Started a on_voice_state_update at {datetime.datetime.now()}")
  if member.bot: #Quick and easy out if the event is caused by a bot
    return
  SpecialChannelName = 'Round Up A Posse'
  
  # Making named booleans for code visibility 
  afterExists = after is not None and after.channel is not None
  afterIsPosseChannel = afterExists and after.channel.name == SpecialChannelName 
  nobodyInAfterChannel = afterExists and len(after.channel.voice_states) == 0
  beforeExists = before is not None and before.channel is not None
  beforeIsPosseChannel = beforeExists and before.channel.name == SpecialChannelName 
  nobodyInBeforeChannel = beforeExists and len(before.channel.voice_states) == 0
  randomSoundChance = random.random() <= .1 #10% chance
  
  # Make a new channel if the user joins the special channel
  if afterExists and afterIsPosseChannel: # dont want things to trigger in posse channel
    print(f"Started the process of making a new channel at {datetime.datetime.now()}")
    overwrites = {}
    guild = after.channel.guild
    userData = getUserData(member.id)
    
    # If we have a posse list for the user lets go in and make custom overwrites for the channel
    if userData["PosseList"]: 
      overwriteMemberList = []
      for i in userData["PosseList"]:
        overwriteMemberList.append(bot.get_user(i))
      # Lets go out and actually make the overwrites object
      overwrites = {
        guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=False),
        # This is the "Townspeople" role
        guild.get_role(891126367498928148): discord.PermissionOverwrite(connect=False, view_channel=False),
        member: discord.PermissionOverwrite(connect=True, view_channel=True)
      }
      for i in overwriteMemberList:
        overwrites[i] = discord.PermissionOverwrite(connect=True, view_channel=True)
    categoryChannel = guild.get_channel(887583365442715708) # Outside of Town
    channelName = (userData["PosseName"] if userData["PosseName"] else (member.nick if member.nick else member.name))
    newChannel = await guild.create_voice_channel(name=channelName, bitrate=128000, category=categoryChannel, overwrites=overwrites)
    await member.move_to(channel=newChannel)
    
  # Delete voice channels if no one is in them after state updates and they are not the Special name
  if afterExists and not afterIsPosseChannel and nobodyInAfterChannel:
    print(f"Started the process of deleting a channel at {datetime.datetime.now()}")
    await after.channel.delete()
  if beforeExists and not beforeIsPosseChannel and nobodyInBeforeChannel:
    print(f"Started the process of deleting a channel at {datetime.datetime.now()}")
    await before.channel.delete()
      
  # Lets have a random chance to make a sound on entry
  if randomSoundChance and afterExists and not beforeExists and not afterIsPosseChannel:
    print(f"Started the process of making random noise at {datetime.datetime.now()}")
    
    # Lets disconnect the bot from all the voice channels they are currently in 
    for i in bot.voice_clients:
      await i.disconnect(force=True)
      
    # Connect to the channel we want the bot in and play the sound
    vc = await after.channel.connect()
    soundFileName = random.choice(['TheGoodtheBadandtheUgly.mp3','PumpkinCowboy.mp3']) # Add to this list later
    vc.play(discord.FFmpegPCMAudio(soundFileName,options='-filter:a "volume=0.4"'))
    
    # Wait a bit and disconnect
    time.sleep(5)
    await vc.disconnect(force=True)
  #print(f"Ended a on_voice_state_update at {datetime.datetime.now()}")

###########
## Games ##
###########
  
@bot.slash_command(guild_ids=servers, name="love_letter", description="play a game of love letter")
async def loveletter(ctx, member1: discord.Option(discord.Member, required=True), 
                          member2: discord.Option(discord.Member, required=False), 
                          member3: discord.Option(discord.Member, required=False)):
  print(f"Started a love letter at {datetime.datetime.now()}")
  await ctx.respond(content="Started an LL game with  " + ", ".join([str(i) for i in [member1,member2,member3] if i]) + " ", ephemeral=True)
  
##################
## Other Things ##
##################

@bot.event
async def on_ready():
  print(f'{bot.user} has connected to Discord at {datetime.datetime.now()}')
  
@bot.event
async def on_presence_update(before, after):
  print(f"Started a on_presence_update at {datetime.datetime.now()}")
  if after.status == 'streaming':
    for channel in await bot.fetch_channel(887583365442715708).channels: # Channels in "Outside of Town" Category Channel
      if channel.ChannelType == 'voice' and after in channel.members:
        await channel.edit(name=f"(Streaming) {channel.name}", reason=f"{after.name} started streaming")
        return

@bot.listen()
async def on_message(message):
  if message.content[:13] == "Hey Mr. Hand!":
    await message.channel.send("Dont anger that which you don't understand")
  if message.channel.type == 'text' and message.channel.name == "post-office" and datetime.datetime.now().weekday() == 6:
    await message.channel.send("https://tenor.com/view/no-post-on-sunday-vernon-dursley-sundays-harry-potter-gif-10875689")

bot.run(secret_token)
