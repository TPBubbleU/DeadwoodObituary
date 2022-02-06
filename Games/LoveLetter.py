import random, pickle

class LLCard:
	def __init__(self, name, description, value):
		self.name = name
		self.description = description
		self.value = value	
		
GUARD_DESC = "Player designates another player and names a type of card. If that players hand matches the type of card specified, that player is eliminated from the round. However, Guard cannot be named as the type of card."
PRIEST_DESC = "Player is allowed to see another player's hand."
BARON_DESC = "Player will choose another player and privately compare hands. The player with the lower-strength hand is eliminated from the round."
HANDMAID_DESC = "Player cannot be affected by any other player's card until the next turn."
PRINCE_DESC = "Player can choose any player (including themselves) to discard their hand and draw a new one. If the discarded card is the Princess, the discarding player is eliminated."
KING_DESC = "Player trades hands with any other player."
COUNTESS_DESC = "If a player holds both this card and either the King or Prince card, this card must be played immediately."
PRINCESS_DESC = "If a player plays this card for any reason, they are eliminated from the round."

class LLDeck:
	def __init__(self):
		self.cards = [
			LLCard("Guard",GUARD_DESC,1),
			LLCard("Guard",GUARD_DESC,1),
			LLCard("Guard",GUARD_DESC,1),
			LLCard("Guard",GUARD_DESC,1),
			LLCard("Guard",GUARD_DESC,1),
			LLCard("Priest",PRIEST_DESC,2),
			LLCard("Priest",PRIEST_DESC,2),
			LLCard("Baron",BARON_DESC,3),
			LLCard("Baron",BARON_DESC,3),
			LLCard("Handmaid",HANDMAID_DESC,4),
			LLCard("Handmaid",HANDMAID_DESC,4),
			LLCard("Prince",PRINCE_DESC,5),
			LLCard("Prince",PRINCE_DESC,5),
			LLCard("King",KING_DESC,6),
			LLCard("Countess",COUNTESS_DESC,7),
			LLCard("Princess",PRINCESS_DESC,8),
		]
		random.shuffle(self.cards)
		# Take one card out so people can't card count 
		self.cards.pop()
	
	def TopCard(self):
		return self.cards.pop()
	
class LLPlayer:
	def __init__(self, name=None, discordUser=None):
		self.name = name
		self.discordUser = discordUser
		self.hand = []
		self.played = []
		self.tokens = 0
		self.out = False
		self.turn = False
		self.handmaided = False
		self.targeted = None
		self.firstTarget = None

class LLGame:
  def __init__(self, discords):
    # This list of messages is we will get information about what has happened in the game
    self.messages = [LLMessage("The game has started!")]

    # Setup the Deck
    self.deck = LLDeck()

    # Setup the players
    self.players = []
    for i in range(len(discords)):
      self.players.append(LLPlayer(discords[i],i))
    random.shuffle(self.cards) # lets get a random order of players
    self.players[0].turn = True
    # Each player starts with a card
    for player in self.players:
      card = self.deck.TopCard()
      player.hand.append(card)
      self.messages.append(LLMessage(f"Your first card is {card}", player, card.file))

    # It's first players turn they draw a card
    # Display out for first play
    self.messages.append(LLMessage(f"{self.players[0]} has the first turn "))
    card = self.deck.TopCard()
    self.players[0].hand.append(card)
    self.messages.append(LLMessage(f"You drew a {card}", player, card.file))
        
  def WhatsNext(self):
    player = [x for x in self.players if x.turn][0] # player whose turn it is
    if player.targeted:
      return f"Player {player} needs to guess a card for his guard"
    elif len(player.hand) == 1:
      return f"Player {player} needs to target a player"
    else:
      return f"Player {player} needs to choose a card to play"
        
  def GetWhoseTurnItIs(self,cycle=True):
    player = [x for x in self.players if x.turn][0] # player whose turn it is
    # If we arent trying to cycle to the next players turn were done here lets take an early out
    if not cycle:
      return player
    # Set it to not be their turn 
    player.turn = False
    # Lets get a list of other players who are still in the game and not the player whose turn it was
    playersStillIn = [x for x in self.players if x.out != True and x != player]
    # Lets get the lowest rank of players that has yet to play in this round 
    desiredRank = min([x.rank for x in playersStillIn if x.rank > player.rank])
    # If that doesn't exist then the lowest rank player of those still in is who we want
    if not desiredRank:
      desiredRank = min([x.rank for x in playersStillIn])
    # Lets get the player with that desired rank
    nextTurnPlayer = [x for x in playersStillIn if x.rank == desiredRank][0]
    # Continue looping through to find next player whose turn it is 
    nextTurnPlayer.turn = True
    nextTurnPlayer.handmaided = False
    return nextTurnPlayer
            
  # This method is only called inside the Action method or Actions Sub methods for ending the turn
  def ActionTurnOver(self, player):
    # Reset the old targetting 
    player.targeted = None
    # Check to see if round is over
    if not self.deck.cards:
      print("Cards are all gone, the round is now over")
      self.RoundIsOver()
      self.NewRoundSetup()
      return
    # If there is only one player lets award him a token and end the round    
    playersin = [player for player in self.players if not player.out]
    if len(playersin) == 1:
      print(playersin[0].name + " is the last player in and has won the round")
      playersin[0].tokens = playersin[0].tokens + 1
      self.NewRoundSetup()
      return
    # Get whose turn it is and cycle to next one
    newplayer = self.GetWhoseTurnItIs(cycle=True)
    print("It is now " + newplayer.name + "'s turn")
    # Give that player a new card
    newplayer.hand.append(self.deck.TopCard())
    # Display hand out for next turn
    handnames = [i.name for i in newplayer.hand]
    print(newplayer.name + " has the hand of: ")
    print("1: " + newplayer.hand[0].name)
    print("2: " + newplayer.hand[1].name)
    # Check for the Countess AutoPlay
    if ("Countess" in handnames) and (("Prince" in handnames) or ("King" in handnames)):
      print("Regardless of your choice you are forced to play the countess")
      print("We still will wait for a response so you can bluff that this wasn't forced")

  # This method is only called inside the Action method for card guessing for Guard
  def ActionGuardGuess(self, player, text):
    if int(text) == player.targeted.hand[0].value:
      print(player.targeted.name + " is now out")
      player.targeted.out = True
    else:
      print("Nothing Happened")
    self.ActionTurnOver(player)
        
  # This method is only called inside the Action method for targetting
  def ActionTargetting(self, player, text):
    # Make list of targetted players
    targetplayers = [x for x in self.players if not x.out and not x.handmaided]
    # Quick validation of text supplied
    try:
      text = int(text)
      if text not in range(1, len(targetplayers)+1):
        raise ValueError()
    except:
      print("You typed something wrong, nothing happened")
    player.targeted = targetplayers[int(text) - 1]
    # Lets do a large if statement to figure out which card was played for the targetting
    # Guard was played last
    if player.played[-1].value == 1:
      print("Please guess a card by using one of the following numbers")
      print("2: Preist\n3: Baron\n4: Handmaid\n5: Prince\n6: King\n7: Countess\n8: Princess")
      return
    # Priest was played Last
    elif player.played[-1].value == 2:
      print(player.targeted.name + " has a " + player.targeted.hand[0].name)
    # Baron was played last
    elif player.played[-1].value == 3:
      if player.targeted.hand[0].value > player.hand[0].value:
        print(player.name + " is now out")
        player.out = True
      elif player.hand[0].value > player.targeted.hand[0].value:
        print(player.targeted.name + " is now out")
        player.targeted.out = True
      else:
        print("Nothing happened")
    # Prince was played last
    elif player.played[-1].value == 5:
      print(player.targeted.name + " discarded " + player.targeted.hand[0].name)
      if player.targeted.hand[0].name == "Princess":
        print(player.targeted.name + " is now out of the round")
        player.targeted.out = True
        self.ActionTurnOver(player)
        return
      player.targeted.hand[0] = self.deck.TopCard()
      print(player.targeted.name + " got a new card of " + player.targeted.hand[0].name)
    # King was played last
    elif player.played[-1].value == 6:
      swap = player.hand[0]
      player.hand[0] = player.targeted.hand[0]
      player.targeted.hand[0] = swap
      print(player.name + "'s new card is " + player.hand[0].name)
      print(player.targeted.name + "'s new card is " + player.targeted.hand[0].name)
    self.ActionTurnOver(player)
  
  # This method is only called inside the Action method for targetting
  def ActionCardPlay(self, player, text):
    # Quick validation of text supplied
    try:
      text = int(text)
      if text not in [1,2]:
        raise ValueError()
    except:
      print("You typed something wrong, nothing happened")
    # Countess force play check
    handnames = [i.name for i in player.hand]
    if ("Countess" in handnames) and (("Prince" in handnames) or ("King" in handnames)):
      if "Countess" == handnames[0]:
        cardplayed = player.hand.pop(0)
      else: 
        cardplayed = player.hand.pop(1)
     # Selected Card comes out of the hand and is played
    else:
      cardplayed = player.hand.pop(int(text) - 1)
      player.played.append(cardplayed)
    print(player.name + " has played " + cardplayed.name)
    # Take Action depending on what was played
    if cardplayed.name in ["Guard","Preist","Baron","Prince","King"]:
      # Display text for targetting 
      print("Please target a player by using one of the following numbers")
      targetplayers = [i for i in self.players if (not i.out) and (not i.handmaided)]
      for i in range(len(targetplayers)):
        print(str(i+1) + ": " + targetplayers[i].name)
    elif cardplayed.name == "Handmaid":
      player.handmaided = True
      self.ActionTurnOver(player)
    elif cardplayed.name == "Countess":
      self.ActionTurnOver(player)
    elif cardplayed.name == "Princess":
      print("Why would you do this? You're now out of the round")
      player.out = True
      self.ActionTurnOver(player)
  
  # This is about taking an action and pushing the game to a state where it needs a new action
  def Action(self, playername, text):
    player = self.GetWhoseTurnItIs(cycle=False)
    if not playername == player.name:
      print("It's not your turn though")
      return
    if player.targeted:
      # We know that what needs to happen next is to select a card to guard
      self.ActionGuardGuess(player, text)
    elif len(player.hand) == 1:
      # We know that what needs to happen next is the player needs to target a player
      self.ActionTargetting(player, text)
    else:
      # We know that what needs to happen next is the player needs to play a card
      self.ActionCardPlay(player, text)
  
  def NewRoundSetup(self):
    print('Starting a new round')
    self.deck = LLDeck()
    for player in self.players:
      player.played = []
      player.out = False
      player.hand = []
      player.hand.append(self.deck.TopCard())
    self.players[0].turn = True
    print("It is now " + self.players[0].name + "'s turn")
    # Give that player a new card
    self.players[0].hand.append(self.deck.TopCard())
    # Display hand out for next turn
    handnames = [i.name for i in self.players[0].hand]
    print(self.players[0].name + " has the hand of: ")
    print("1: " + self.players[0].hand[0].name)
    print("2: " + self.players[0].hand[1].name)
    # Check for the Countess AutoPlay
    if ("Countess" in handnames) and (("Prince" in handnames) or ("King" in handnames)):
      print("Regardless of your choice you are forced to play the countess")
      print("We still will wait for a response so you can bluff that this wasn't forced")
  
  def RoundIsOver(self):
    HighCard = []
    for player in self.players:
      print(player.name + " has the last card of: " + player.hand[0].name)
      if not HighCard:
        HighCard.append(player)
      elif player.hand[0].value > HighCard[0].hand[0].value:
        HighCard = [player]
      elif player.hand[0].value == HighCard[0].hand[0].value:
        HighCard.append(player)

    if len(HighCard) != 1:
      print("Looks like we have a tie on our hands it's between ")
      print(" and ".join([i.name for i in HighCard]))
      WinTotal = []
      for player in HighCard:
        CurrentPlayerTotal = sum([i.value for i in player.played])
        print(player.name + " has played a value of: " + str(CurrentPlayerTotal))
        if not WinTotal:
          WinTotal.append(player)
        elif CurrentPlayerTotal > sum([j.value for j in WinTotal[0].played]):
          WinTotal = [player]
        elif CurrentPlayerTotal == sum([j.value for j in WinTotal[0].played]):
          WinTotal.append(player)

      if len(WinTotal) != 1:
        print("Looks like we still have a tie on our hands it's between ")
        print(" and ".join([i['name'] for i in WinTotal]))
        print("I forgot what you're supposed to do here though LOL")
        print("They all get a token.... right?")
        for player in WinTotal:
          player.tokens = player.tokens + 1
      else:
        print("We have a winner of " + WinTotal[0].name)
        WinTotal[0].tokens = WinTotal[0].tokens + 1
    else:
      print("We have a winner of " + HighCard[0].name)
      HighCard[0].tokens = HighCard[0].tokens + 1
    self.NewRoundSetup()
