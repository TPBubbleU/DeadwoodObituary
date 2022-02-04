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
	def GetWhoseTurnItIs(self,cycle=True):
		# Loop through all players
		for i in range(len(self.players)):
			# Find out whose turn it was last
			if self.players[i].turn == True:
				# If we arent trying to cycle to the next players turn were done here
				if not cycle:
					return self.players[i]
				# Set it to not be their turn 
				self.players[i].turn = False
				# Continue looping through to find next player whose turn it is 
				for j in range(i + 1,len(self.players)):
					if self.players[j].out == False:
						self.players[j].turn = True
						self.players[j].handmaided = False
						return self.players[j]
				else:
					# It wasn't in the rest of the array so lets start from the begining
					for j in range(i):
						if self.players[j].out == False:
							self.players[j].turn = True
							self.players[j].handmaided = False
							return self.players[j]

	def StartOfTurn(self, cycle=False):
		# Get whose turn it is with the option to cycle to next one
		player = self.GetWhoseTurnItIs(cycle)
		self.messages.append({'who':'all','message':"It is now " + player.name + "'s turn"})
		# That player draws a card
		player.hand.append(self.deck.TopCard())
		# Display out for first play
		handnames = [i.name for i in player.hand]
		self.messages.append({'who':player,'message':"You has the hand of: "})
		self.messages.append({'who':player,'message':"1: " + player.hand[0].name})
		self.messages.append({'who':player,'message':"2: " + player.hand[1].name})
		self.messages.append({'who':player,'message':"You can play these by using the command \"!Action 1\" or \"!Action 2\""})
		# Check for the Countess AutoPlay
		if ("Countess" in handnames) and (("Prince" in handnames) or ("King" in handnames)):
			self.messages.append({'who':player,'message':"Regardless of your choice you are forced to play the countess"})
			self.messages.append({'who':player,'message':"We still will wait for a response so you can bluff that this wasn't forced"})

	def __init__(self, users):
		self.messages = []
		self.players = []
		for i in users:
			self.players.append(LLPlayer(str(i), i))
		self.players[0].turn = True
		self.deck = LLDeck()
		# Each player starts with a card
		for player in self.players:
			player.hand.append(self.deck.TopCard())
		self.messages.append({'who':'all','message':"The game has started!"})
		self.StartOfTurn(cycle=False)
		
	def WhatsNext(self):
		player = self.GetWhoseTurnItIs()
		if player.targeted:
			self.messages.append({'who':'all','message':"Player " + player.name + " needs to guess a card for his guard"})
		elif len(player.hand) == 1:
			self.messages.append({'who':'all','message':"Player " + player.name + " needs to target a player"})
		else:
			self.messages.append({'who':'all','message':"Player " + player.name + " needs to choose a card to play"})
		
	def WhatsTheScore(self):
		for player in self.players:
			self.messages.append({'who':'all','message':"Player " + player.name + " has " + str(player.tokens) + " tokens"})
			
	def CardDescription(self, playername):
		for player in self.players:
			if playername == player.name:
				break
		else:
			self.messages.append({'who':'all','message':"I don't have you as playing though"})
			return
		for card in player.hand:
			self.messages.append({'who':player,'message':card.name + ": " + card.description})
			
	# This method is only called inside the Action method or Actions Sub methods for ending the turn
	def ActionTurnOver(self, player):
		# Special code for clearing Sycophant
		for i in self.players:
			if player.played[-1].name != 'Sycophant' and player.targeted is not None and player.targeted.name != i.name:
				i.sycophant = False
		# Reset the old targetting 
		player.targeted = None
		player.firstTarget = None
		# Check to see if round is over
		if not self.deck.cards:
			self.messages.append({'who':'all','message':"Cards are all gone, the round is now over"})
			winner = self.RoundIsOver()
			self.NewRoundSetup(winner=winner)
			return
		# If there is only one player lets award him a token and end the round	
		playersin = [player for player in self.players if not player.out]
		if len(playersin) == 1:
			self.messages.append({'who':'all','message':playersin[0].name + " is the last player in and has won the round"})
			playersin[0].tokens = playersin[0].tokens + 1
			self.NewRoundSetup(winner=playersin[0])
			return
		self.StartOfTurn(cycle=True)

	# This method is only called inside the Action method for card guessing for Guard
	def ActionCardGuess(self, player, text):
		if player.played[-1].name == "Guard":
			lownumber = 2
		else: # Bishop was last played
			lownumber = 1
		# Quick validation of text supplied
		try:
			text = int(text)
			if text not in range(lownumber,9):
				raise ValueError()
		except:
			self.messages.append({'who':'all','message':"You typed something wrong, nothing happened"})
		if player.played[-1].name == "Guard":
			if int(text) == player.targeted.hand[0].value:
				self.messages.append({'who':'all','message':player.targeted.name + " is now out"})
				player.targeted.out = True
			else:
				self.messages.append({'who':'all','message':"Wrong guess, nothing happened"})
		else: # Bishop was last played
			if int(text) == player.targeted.hand[0].value:
				self.messages.append({'who':'all','message':"You have guessed correctly and have gained a token of affection"})
				player.tokens = player.tokens + 1
			else:
				self.messages.append({'who':'all','message':"You have guessed incorrectly, nothing happened"})
				
		self.ActionTurnOver(player)
		
	# This method is to put repeated code into one place
	def GetTargetablePlayers(self, player):
		targetplayers = []
		for i in self.players:
			if (not i.out) and (not i.handmaided):
				if player.firstTarget is not None:
					if (i.name != player.firstTarget.name):
						targetplayers.append(i)
				else:
					targetplayers.append(i)
		return targetplayers
	
	# This method is only called inside the Action method for targetting
	def ActionTargetting(self, player, text):
		# Make list of targetted players
		targetplayers = self.GetTargetablePlayers(player)
		# Quick validation of text supplied
		try:
			text = int(text)
			if text not in range(1, len(targetplayers)+1):
				raise ValueError()
		except:
			self.messages.append({'who':'all','message':"You typed something wrong, nothing happened"})
		player.targeted = targetplayers[int(text) - 1]
		
		# Lets do a large if statement to figure out which card was played for the targetting
		# ##################### #
		# Guard was played last #
		# ##################### #
		if player.played[-1].name == "Guard":
			if player.targeted.hand[0].name == 'Assassin':
				self.messages.append({'who':'all','message':player.targeted.name + " was an Assassin, " + play.name + " is now out"})
				player.targeted.hand.pop(0)
				# Check if there are cards to see if player can get a new hand
				if self.deck.cards:
					player.targeted.hand.append(self.deck.TopCard())
					self.messages.append({'who':player.targeted,'message':"You were forced to draw a new card"})
					self.messages.append({'who':player.targeted,'message':"It's a " + player.targeted.hand[0].name})
					return
				else:
					self.messages.append({'who':'all','message':"Bad stroke of luck, no more cards, " + player.targeted + " is out"})
					player.targeted.out = True
					return
			self.messages.append({'who':'all','message':"Please guess a card by using one of the following numbers"})
		  self.messages.append({'who':'all','message':"2: Priest\n3: Baron\n4: Handmaid\n5: Prince\n6: King\n7: Countess\n8: Princess"})
			return
			
		# ###################### #
		# Priest was played Last #
		# ###################### #
		elif player.played[-1].name == 'Priest':
			self.messages.append({'who':player,'message':player.targeted.name + " has a " + player.targeted.hand[0].name})
			
		# ##################### #
		# Baron was played last #
		# ##################### #
		elif player.played[-1].name == 'Baron':
			if player.targeted.hand[0].value > player.hand[0].value:
				self.messages.append({'who':'all','message':player.name + " is now out"})
				player.out = True
			elif player.hand[0].value > player.targeted.hand[0].value:
				self.messages.append({'who':'all','message':player.targeted.name + " is now out"})
				player.targeted.out = True
			else:
				print("Nothing happened")
				self.messages.append({'who':'all','message':"Nothing Happened"})
			
		# ###################### #
		# Prince was played last #
		# ###################### #
		elif player.played[-1].name == 'Prince':
			self.messages.append({'who':'all','message':player.targeted.name + " discarded " + player.targeted.hand[0].name})
			if player.targeted.hand[0].name == "Princess":
				self.messages.append({'who':'all','message':player.targeted.name + " got Prince'd with a Princess in thier hand and is now out of the round"})
				player.targeted.out = True
				self.ActionTurnOver(player)
				return
			if self.deck.cards:
				player.targeted.hand[0] = self.deck.TopCard()
				self.messages.append({'who':player.targeted,'message':"You got a new card of " + player.targeted.hand[0].name})
			else:
				self.messages.append({'who':'all','message':"Bad stroke of luck, no more cards, " + player.targeted + " is out"})
				player.targeted.out = True
				
		# #################### #
		# King was played last #
		# #################### #
		elif player.played[-1].name == 'King':
			swap = player.hand[0]
			player.hand[0] = player.targeted.hand[0]
			player.targeted.hand[0] = swap
			self.messages.append({'who':player,'message':player.name + "'s new card is " + player.hand[0].name})
			self.messages.append({'who':player.targeted,'message':player.targeted.name + "'s new card is " + player.targeted.hand[0].name})
			
			
		# ###################### #
		# Bishop was played Last #
		# ###################### #
		elif player.played[-1].name == "Bishop":
			self.messages.append({'who':'all','message':"Please guess a card by using one of the following numbers"})
			self.messages.append({'who':'all','message':"0:Assassin/Jester\n1: Guard\n2: Priest/Cardinal\n3: Baron/Baroness\n4: Handmaid/Sycophant\n5: Prince/Count\n6: King/Constable\n7: Countess/Dowager Queen\n8: Princess"})
			return
			
		self.ActionTurnOver(player)
	
	# This method is only called inside the Action method for targetting
	def ActionCardPlay(self, player, text):
		# Quick validation of text supplied
		try:
			text = int(text)
			if text not in [1,2]:
				raise ValueError()
		except:
			self.messages.append({'who':'all','message':"You typed something wrong, nothing happened"})
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
		self.messages.append({'who':'all','message':player.name + " has played " + cardplayed.name})
		# Take Action depending on what was played
		if cardplayed.name in ["Jester","Guard","Priest","Cardinal","Baron","Baroness","Sycophant","Prince","King","Dowager Queen","Bishop"]:
			# Display text for targetting 
			self.messages.append({'who':'all','message':"Please target a player by using one of the following numbers"})
			targetplayers = self.GetTargetablePlayers(player)
			for i in range(len(targetplayers)):
				self.messages.append({'who':'all','message':str(i+1) + ": " + targetplayers[i].name})
			if cardplayed.name == "Cardinal":
				self.messages.append({'who':'all','message':"You will see the card of the first player you target"})
		elif cardplayed.name == "Handmaid":
			player.handmaided = True
			self.ActionTurnOver(player)
		elif cardplayed.name in ["Countess","Assassin","Constable","Count"]:
			self.ActionTurnOver(player)
		elif cardplayed.name == "Princess":
			self.messages.append({'who':'all','message':"Who plays a Princess? " + player.name + " is now out of the round"})
			player.out = True
			self.ActionTurnOver(player)
	
	# This is about taking an action and pushing the game to a state where it needs a new action
	def Action(self, playername, text):
		player = self.GetWhoseTurnItIs(cycle=False)
		if not playername == player.name:
			self.messages.append({'who':'all','message':"It's not your turn though"})
			return
		if player.targeted:
			# We know that what needs to happen next is to select a card to guard
			self.ActionCardGuess(player, text)
		elif len(player.hand) == 1:
			# We know that what needs to happen next is the player needs to target a player
			self.ActionTargetting(player, text)
		else:
			# We know that what needs to happen next is the player needs to play a card
			self.ActionCardPlay(player, text)
	
	def NewRoundSetup(self, winner):
		# Check to see if we have to award tokens for the jester
		if winner.jesterTokenByUser is not None:
			winner.jesterTokenByUser.tokens = winner.jesterTokenByUser.tokens + 1
		# Reset all the things we need to reset
		self.messages.append({'who':'all','message':'Starting a new round'})
		self.deck = LLDeck()
		for player in self.players:
			player.played = []
			player.out = False
			player.handmaided = False
			player.hand = []
			player.hand.append(self.deck.TopCard())
			player.targeted = None
			player.jesterTokenByUser = None
		self.players[0].turn = True
		self.StartOfTurn(cycle=False)
	
	def RoundIsOver(self):
		HighCard = []
		for player in self.players:
			if player.out:
				continue
			self.messages.append({'who':'all','message':player.name + " has the last card of: " + player.hand[0].name})
			if not HighCard:
				HighCard.append(player)
			elif player.hand[0].value > HighCard[0].hand[0].value:
				HighCard = [player]
			elif player.hand[0].value == HighCard[0].hand[0].value:
				HighCard.append(player)

		if len(HighCard) != 1:
			self.messages.append({'who':'all','message':"Looks like we have a tie on our hands it's between "})
			self.messages.append({'who':'all','message':" and ".join([i.name for i in HighCard])})
			WinTotal = []
			for player in HighCard:
				CurrentPlayerTotal = sum([i.value for i in player.played])
				self.messages.append({'who':'all','message':player.name + " has played a value of: " + str(CurrentPlayerTotal)})
				if not WinTotal:
					WinTotal.append(player)
				elif CurrentPlayerTotal > sum([j.value for j in WinTotal[0].played]):
					WinTotal = [player]
				elif CurrentPlayerTotal == sum([j.value for j in WinTotal[0].played]):
					WinTotal.append(player)

			if len(WinTotal) != 1:
				self.messages.append({'who':'all','message':"Looks like we still have a tie on our hands it's between "})
				self.messages.append({'who':'all','message':" and ".join([i['name'] for i in WinTotal])})
				CardTotal = []
				for player in WinTotal:
					self.messages.append({'who':'all','message':player.name + " has played " + str(len(player.played)) + " cards"})
					if not CardTotal:
						CardTotal.append(player)
					elif len(player.played) > len(CardTotal[0].played):
						CardTotal = [player]
					elif len(player.played) == len(CardTotal[0].played):
						CardTotal.append(player)
						
					if len(CardTotal) != 1:
						self.messages.append({'who':'all','message':"Looks like we still have a tie on our hands it's between "})
						self.messages.append({'who':'all','message':" and ".join([i['name'] for i in CardTotal])})
						playersreversed = self.players[::-1]
						for i in playersreversed:
							if i.name in [j.name for j in WinTotal]:
								self.messages.append({'who':'all','message':"We have a winner of " + i.name + " because of turn order" })
								i.tokens = i.tokens + 1
								return i
					else:
						self.messages.append({'who':'all','message':"We have a winner of " + CardTotal[0].name})
						CardTotal[0].tokens = CardTotal[0].tokens + 1
						return CardTotal[0]
			else:
				self.messages.append({'who':'all','message':"We have a winner of " + WinTotal[0].name})
				WinTotal[0].tokens = WinTotal[0].tokens + 1
				return WinTotal[0]
		else:
			self.messages.append({'who':'all','message':"We have a winner of " + HighCard[0].name})
			HighCard[0].tokens = HighCard[0].tokens + 1
			return HighCard[0]
