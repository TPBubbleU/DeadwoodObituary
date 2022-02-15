import discord, datetime, asyncio, os, random, time, requests
from discord.ext import commands
from discord.ui import Button, View, InputText, Modal, Select
from gtts import gTTS 
from urllib.parse import quote
from threading import Timer
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
  if afterExists and not afterIsPosseChannel and member.status == discord.Status.streaming: # and after.channel.name[:11] != '(Streaming)'
    print(f"Adding streaming prefix to channel {after.channel.name} at {datetime.datetime.now()}")
    await channel.edit(name=f"(Streaming) {after.channel.name}", reason=f"{member.name} started streaming")
    
  #print(f"Ended a on_voice_state_update at {datetime.datetime.now()}")

###########
## Games ##
###########
  
# @bot.slash_command(guild_ids=servers, name="love_letter", description="play a game of love letter")
# async def loveletter(ctx, member1: discord.Option(discord.Member, required=True), 
#                           member2: discord.Option(discord.Member, required=False), 
#                           member3: discord.Option(discord.Member, required=False)):
#   print(f"Started a love letter at {datetime.datetime.now()}")
#   await ctx.respond(content="Started an LL game with  " + ", ".join([str(i) for i in [member1,member2,member3] if i]) + " ", ephemeral=True)
  
#############
## Spotify ##
#############
  
@bot.slash_command(guild_ids=servers, name="spotify", description="Give chat control of your spotify")
async def spotify(ctx):
  print(f"Started a spotify controller at {datetime.datetime.now()}")
  # Lets build our setup variables
  redirect = 'https://script.google.com/macros/s/AKfycbwQYNT3PFFuArWNXf5u4fc4R0tsKoC2fWJ2SneOQ-Jpn1sfD-AG/exec'
  clientId = '19b73b32826642e19f33a70678a59ea5'
  scopes = 'user-read-private user-read-currently-playing user-modify-playback-state user-read-playback-position'
  setup_url = f'https://accounts.spotify.com/authorize?response_type=code&client_id={clientId}&scope={quote(scopes)}&redirect_uri={quote(redirect)}'
  userData = getUserData(ctx.author.id) # This sets up the user if they are not in memory already
  
  # Lets setup a method of getting a little embed object of what is currently playing so we can call it lots
  def get_current_song_embed():
    embed = discord.Embed(title="Currently Playing",color=discord.Color.blurple())
    # Get currently playing endpoint from spotify
    headers = {'Authorization': 'Bearer ' + UsersLists[ctx.author.id]['SpotifyAccess']}
    sresponse = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers)
    if sresponse.status_code == 204:
      embed.add_field(name="Song Name:", value="Can't currently find anything playing")
      return embed
    current_song = sresponse.json()
    # Build a whole embed with details from the song 
    embed.add_field(name="Song Name:", value=current_song['item']['name'], inline=True)
    embed.add_field(name="Album:", value=current_song['item']['album']['name'], inline=True)
    embed.add_field(name="Artist(s):", value=", ".join([x['name'] for x in current_song['item']['artists']]), inline=True)
    embed.add_field(name="Link:", value=current_song['item']['external_urls']['spotify'], inline=True)
#     # Lets setup a method to wait and then update the currently playing on our embed
#     wait_time = current_song['item']['duration_ms'] - current_song['progress_ms'] + 2000
#     async def refresh_embeds():
#       embed = get_current_song_embed()
#       await ctx.interaction.edit_original_message(embeds=[embed])
#     timer = Timer(wait_time, refresh_embeds())
#     timer.start()
    return embed  
  
  # Setup the last song button and callback for later
  last_song_button = Button(label="last song")
  async def last_song_callback(interaction):
    requests.post('https://api.spotify.com/v1/me/player/previous', headers={'Authorization': 'Bearer ' + UsersLists[ctx.author.id]['SpotifyAccess']})
    time.sleep(1) # Lets give Spotify a tiny bit of time to actually change the song
    embed = get_current_song_embed()
    await ctx.interaction.edit_original_message(embeds=[embed])
  last_song_button.callback = last_song_callback
  
  # Setup the next song button and callback for later
  next_song_button = Button(label="next song")
  async def next_song_callback(interaction):
    requests.post('https://api.spotify.com/v1/me/player/next', headers={'Authorization': 'Bearer ' + UsersLists[ctx.author.id]['SpotifyAccess']})
    time.sleep(1) # Lets give Spotify a tiny bit of time to actually change the song
    embed = get_current_song_embed()
    await ctx.interaction.edit_original_message(embeds=[embed])
  next_song_button.callback = next_song_callback
  
  # Setup the queue a song button and callback for later
  queue_song_button = Button(label="Queue song")
  async def queue_song_callback(interaction):
    search_modal = Modal(title="Lets search")
    search_modal.add_item(InputText(label="What track are we searching for: "))
    async def callback_for_modal(interaction):
      headers = {'Authorization': 'Bearer ' + UsersLists[ctx.author.id]['SpotifyAccess']}
      params = {'q':search_modal.children[0].value, 'type':'track', 'limit':10}
      sresponse = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)
      results = sresponse.json()
      options = []
      for track in results['tracks']['items']:
        artists = ", ".join([x['name'] for x in track['artists']])
        options.append(discord.SelectOption(label=track['name'], 
                                            description=f"Artist: {artists} Album:{track['album']['name']}",
                                            value=track['uri']))
      search_select = discord.ui.Select(placeholder="Pick Your Modal", min_values=1, max_values=1, options=options)
      async def search_select_callback(interaction):
        headers = {'Authorization': 'Bearer ' + UsersLists[ctx.author.id]['SpotifyAccess']}
        params = {'uri':search_select.values[0]}
        sresponse = requests.post("https://api.spotify.com/v1/me/player/queue", headers=headers, params=params)
        await interaction.edit_original_message(content="Added to queue")
      search_select.callback = search_select_callback
      search_view = View(search_select, timeout=None)
      await ctx.interaction.followup.send(content="Here is what we found", ephemeral=True, view=search_view)
      
    search_modal.callback = callback_for_modal
    await interaction.response.send_modal(search_modal)
  queue_song_button.callback = queue_song_callback
  
  # Build our command view so other uses can use Spotify Commands
  command_view = View(last_song_button, next_song_button, queue_song_button, timeout=None)
  
  # Lets setup our modal spawning button
  modal_setup_button = Button(label="Give code")
  async def modal_setup_button_click(interaction):
    # Early out if someone else responded other than the orignial slash command user.  
    if (interaction.user != ctx.author):
      interaction.response.send_message("Hey, quit mucking about and do your own slash command", ephemeral=True)
      return 
    # Lets build a Modal because this seems to be one of the few ways of getting input text from a user
    setup_modal = Modal(title="Auth code getter")
    setup_modal.add_item(InputText(label="Enter key here: ", min_length=10))
    async def callback_for_modal(interaction):
      # Setup things to get the access token from Spotifys API
      body = {
        'client_id':clientId,
        'client_secret':spotify_secret,
        'grant_type':'authorization_code',
        'code':setup_modal.children[0].value,
        'redirect_uri':redirect
      }
      auth = requests.post('https://accounts.spotify.com/api/token', data=body)
      print(auth.text)
      #print(auth.json()['access_token'])
      # Save our access token into our user list object
      UsersLists[ctx.author.id]['SpotifyAccess'] = auth.json()['access_token']
      # Lets update our original message
      content = f"{ctx.author} has decided to live dangerously and give control of his spotify to chat "
      embed = get_current_song_embed()
      await ctx.interaction.edit_original_message(content=content, view=command_view, embeds=[embed])
      # Lets respond to the modal interaction so it doesn't say it failed
      await interaction.response.send_message("", delete_after=0) 
    setup_modal.callback = callback_for_modal
    await interaction.response.send_modal(setup_modal)
  modal_setup_button.callback = modal_setup_button_click
  
  # Lets build a view with our predefined modal spawning button and link to get the auth code
  setup_view = View(Button(label="Get Code", url=setup_url), modal_setup_button, timeout=None)
  await ctx.respond(content=f"Lets start by getting you setup \nGo get a code from Spotify and give it back", view=setup_view)
  
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
  if after.status == discord.Status.streaming:
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
