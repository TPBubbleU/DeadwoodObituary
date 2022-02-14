import discord, datetime, asyncio, os, random, time
from discord.ext import commands
from discord.ui import Button, View, InputText, Modal
from gtts import gTTS 
import requests
from urllib.parse import quote
#from Games.LoveLetter import LLGame

try:  
  os.environ["DISCORD_BOT_TOKEN"]
except KeyError: 
  print("Please set the environment variable DISCORD_BOT_TOKEN")
  exit(1)

secret_token = (os.environ["DISCORD_BOT_TOKEN"])
spotify_secret = (os.environ["SPOTIFY_CLIENT_SECRET"])

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

# # Nick Testing things
# @bot.slash_command(guild_ids=servers, name="the-big-test", description="TPBubbleU is messing around")
# async def bigtest(ctx, text: discord.Option(str, required=True)):
#   print(f"Started a test command at {datetime.datetime.now()} ")
#   interaction = await ctx.respond(content=f"Saying '{text}' ", ephemeral=True)
#   time.sleep(5)
#   await interaction.edit_original_message(content="We changed the thing")
  
@bot.slash_command(guild_ids=servers, name="the-hands-voice", description="Make the hand say something in a voice")
async def renameposse(ctx, channel: discord.Option(discord.VoiceChannel, required=True)
                         , text: discord.Option(str, required=True)):
  print(f"Started a say command at {datetime.datetime.now()} for {ctx.author} channel of {channel} text of {text}")
  interaction = await ctx.respond(content=f"Saying '{text}' to channel '{channel}'", ephemeral=True)
  # Lets make and save a voice to text mp3
  gTTS(text=text, lang='en', slow=False).save("voicechat.mp3")
  # Connect and play the file
  vc = await channel.connect()
  player = vc.play(discord.FFmpegPCMAudio(source="voicechat.mp3"))
  # Wait until the file is done playing
  while vc.is_playing():
    time.sleep(1)
  # stop the playback disconnect 
  vc.stop()
  await vc.disconnect()

##################################
## Secret Discord Voices Things ##
##################################

def getUserData(id):
  if id not in UsersLists.keys():
    UsersLists[id] = {"PosseList":[],"PosseName":None, "SpotifyAccess":None}
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
    overwrites = {member: discord.PermissionOverwrite(connect=True, view_channel=True, manage_channels=True)}
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
        member: discord.PermissionOverwrite(connect=True, view_channel=True, manage_channels=True)
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
    
  # Special Consideration for someone joining a channel that has already started streaming and the channels name doesn't start with streaming
  if afterExists and not afterIsPosseChannel and member.status == 'streaming': # and after.channel.name[:11] != '(Streaming)'
    print(f"Adding streaming prefix to channel {after.channel.name} at {datetime.datetime.now()}")
    await channel.edit(name=f"(Streaming) {after.channel.name}", reason=f"{member.name} started streaming")
    
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
  
#############
## Spotify ##
#############
  
@bot.slash_command(guild_ids=servers, name="spotify", description="Give chat control of your spotify")
async def spotify(ctx):
  print(f"Started a spotify controller at {datetime.datetime.now()}")
  redirect = 'https://script.google.com/macros/s/AKfycbwQYNT3PFFuArWNXf5u4fc4R0tsKoC2fWJ2SneOQ-Jpn1sfD-AG/exec'
  clientId = '19b73b32826642e19f33a70678a59ea5'
  scopes = 'user-read-private user-read-currently-playing user-modify-playback-state user-read-playback-position'
  link = f'https://accounts.spotify.com/authorize?response_type=code&client_id={clientId}&scope={quote(scopes)}&redirect_uri={quote(redirect)}'
  
  userData = getUserData(ctx.author.id)
  
  response_we_care_about = None
  
  # Lets setup a method of getting a little embed object of what is currently playing so we can call it lots
  def get_current_song_embed():
    current_song = requests.get('https://api.spotify.com/v1/me/player/currently-playing', 
                                headers={'Authorization': 'Bearer ' + UsersLists[ctx.author.id]['SpotifyAccess']}).json()
    embed = discord.Embed(title="Currently Playing",color=discord.Color.blurple())
    embed.add_field(name="Song Name:", value=current_song['item']['name'], inline=True)
    embed.add_field(name="Album:", value=current_song['item']['album']['name'], inline=True)
    embed.add_field(name="Artist(s):", value=", ".join([x['name'] for x in current_song['item']['artists']]), inline=True)
    embed.add_field(name="Link:", value=current_song['item']['external_urls']['spotify'], inline=True)
    return embed  
  
  # Setup the last song button and callback for later
  last_song_button = Button(label="last song")
  async def last_song_callback(interaction):
    #await interaction.response.defer()
    requests.post('https://api.spotify.com/v1/me/player/previous', headers={'Authorization': 'Bearer ' + UsersLists[ctx.author.id]['SpotifyAccess']})
    time.sleep(5)
    embeds = [get_current_song_embed()]
    await interaction.edit_original_message(embeds=embeds)
  last_song_button.callback = last_song_callback
  
  # Setup the next song button and callback for later
  next_song_button = Button(label="next song")
  async def next_song_callback(interaction):
    #await interaction.response.defer()
    requests.post('https://api.spotify.com/v1/me/player/next', headers={'Authorization': 'Bearer ' + UsersLists[ctx.author.id]['SpotifyAccess']})
    time.sleep(5)
    embeds = [get_current_song_embed()]
    await interaction.edit_original_message(embeds=embeds)
  next_song_button.callback = next_song_callback
  
  command_view = View(last_song_button, next_song_button, timeout=None)
  
  
  
  # Lets setup our modal spawning button
  modal_spawning_button = Button(label="Click Here for input")
  async def modal_for_button_click(interaction):
    modal = Modal(title="Lets get that input baby!")
    modal.add_item(InputText(label="Enter key here: ", value= 'Get this from the link'))
    async def callback_for_modal(interaction):
      # Setup things to get the access token from Spotifys API
      body = {
        'client_id':clientId,
        'client_secret':spotify_secret,
        'grant_type':'authorization_code',
        'code':modal.children[0].value,
        'redirect_uri':redirect
      }
      auth = requests.post('https://accounts.spotify.com/api/token', data=body).json()
      # Save our access token into our user list object
      UsersLists[ctx.author.id]['SpotifyAccess'] = auth['access_token']
      embeds = [get_current_song_embed()]
      content = f"{ctx.author} has decided to live dangerously and give control of his spotify to chat "
      response_we_care_about = await interaction.response.send_message(content=content, view=command_view, embeds=embeds)
    modal.callback = callback_for_modal
    await interaction.response.send_modal(modal)
  modal_spawning_button.callback = modal_for_button_click
  
  setup_view = View(Button(label="Click Here for link", url=link), modal_spawning_button, timeout=None)
  await ctx.respond(content=f"Lets start by getting you setup \nYou can use this link to get a new auth token", ephemeral=True, view=setup_view)
  
##################
## Other Things ##
##################

@bot.slash_command(guild_ids=servers, name="image_spoiler", description="Add a GOD-DAMNED IMAGE SPOILER")
async def image_spoiler(ctx, text: discord.Option(str, required=False), attachment: discord.Option(discord.Attachment,required=False)):
  print(f"Started a image spoiler command at {datetime.datetime.now()} ")
  attachment.filename = 'SPOILER_' + attachment.filename 
  file = await attachment.to_file()
  await ctx.respond(content=f"{text}", file=file)
    
@bot.event
async def on_ready():
  print(f'{bot.user} has connected to Discord at {datetime.datetime.now()}')
  
@bot.event
async def on_presence_update(before, after):
  if after.status == 'streaming':
    print(f"Started a on_presence_update streaming at {datetime.datetime.now()}")
    for channel in await bot.fetch_channel(887583365442715708).channels: # Channels in "Outside of Town" Category Channel
      if channel.ChannelType == 'voice' and after in channel.members: # and channel.name[:11] != '(Streaming)'
        print(f"Actually chaning the channel name at {datetime.datetime.now()}")
        print(f"Adding streaming prefix to channel {channel.name} at {datetime.datetime.now()}")
        await channel.edit(name=f"(Streaming) {channel.name}", reason=f"{after.name} started streaming")
        return

@bot.listen()
async def on_message(message):
  if message.content[:13] == "Hey Mr. Hand!":
    await message.channel.send("Dont anger that which you don't understand")
  if message.channel.type == 'text' and message.channel.name == "post-office" and datetime.datetime.now().weekday() == 6:
    await message.channel.send("https://tenor.com/view/no-post-on-sunday-vernon-dursley-sundays-harry-potter-gif-10875689")

bot.run(secret_token)
