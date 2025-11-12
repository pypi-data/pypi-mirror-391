import random
import time

def mainloop():
  # learnt new attend function. will be implementing to blackjack soon.
  # stsrted working on "New-game.py", will not be updating since i found out its haram to make.
  # i stsrted workingagain since i dont want you to modify the code.
  def hilo():
    dice1 = random.randint(3, 97)
    choice = input(f"{dice1} Higher Or Lower ")
    dice2 = random.randint(1, 100)
    if choice in ["higher"] and dice1 > dice2:
      time.sleep(0.267)
      print("YOU WoN")
    elif choice in ["lower"] and dice1 < dice2:
      time.sleep(0.267)
      print("You Won!")
      
  def blackjack():
    def stand():
      player_total = firsthand + secondhand + thirdhand + fourthhand + fifthhand + sixthhand + seventhhand
      dt = A1A + B2B
      
      print(f"Player stands with {player_total}")
      print(f"Dealer has: {A1A}, {B2B} Total: {dt}")
      
      dealer_cards = [A1A, B2B]
      while dt < 17:
          time.sleep(0.3)
          new_card = random.choice(card_deck)
          dealer_cards.append(new_card)
          dt += new_card
          
          if dt > 21 and 11 in dealer_cards:
              dt -= 10  
          
          print(f"Dealer Hits {new_card}, now has {dt}")
      
      print(f"Final - Dealer: {dt}, Player: {player_total}")
      
      if dt > 21:
          print("Dealer busts! You win!")
      elif dt > player_total:
          print("Dealer wins!")
      elif dt < player_total:
          print("You win!")
      else:
          print("Push!")
      
      return True  
    def bust():
      FirstPull = False
      SecondPull = False
      ThirdPull = False
      FourthPull = False
      FifthPull = False
      SixthPull = False
      SeventhPull = False
      Bust = False
      
      if (firsthand + secondhand + thirdhand + fourthhand + fifthhand + sixthhand + seventhhand) > 21:
        Bust = True
      if Bust:
        while True:
          print("You Busted (gone over 21!)")
          holder = input("")
    
    playing = True
    while playing:
      playing = False
      firsthand = 0
      secondhand = 0
      thirdhand = 0
      fourthhand = 0
      fifthhand = 0
      sixthhand = 0
      seventhhand = 0
      FBH = 0
      SBH = 0
      TBH = 0
      O4H = 0
      K5B = 0
      card_deck = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 11)
      FirstPull = True
      SecondPull = False
      ThirdPull = False
      FourthPull = False
      FifthPull = False
      SixthPull = False
      SeventhPull = False
      HitOrStand = ""
      s = "succsess message"
      while FirstPull:
        RandomNumber = random.randint(0, 12)
        firsthand = card_deck[RandomNumber]
        RandomNumber = random.randint(0, 12)
        secondhand = card_deck[RandomNumber]
        RandomNumber = random.randint(0, 12)
        A1A = card_deck[RandomNumber]
        RandomNumber = random.randint(0, 12)
        B2B = card_deck[RandomNumber]
        print(f"Your Hand: {firsthand}, {secondhand} Total: {firsthand + secondhand} \n Dealer is Showing {A1A}") 
        bust()
        FirstPull = False
        SecondPull = True
      
      while SecondPull:
        HitOrStand = input("Type \"hit\" To Hit And \"stand\" To Stand")
        if HitOrStand in ["stand"]:
          stand()
        if HitOrStand in ["hit"]:
          RandomNumber = random.randint(0, 12)
          thirdhand = card_deck[RandomNumber]
          print(f"Your Hand: {firsthand}, {secondhand}, {thirdhand} Total: {firsthand + secondhand + thirdhand} \n Dealer is Showing {A1A}")
          bust()
          SecondPull = False
          ThirdPull = True
          bust()
      while ThirdPull:
        userhandtotal = firsthand + secondhand + thirdhand + fourthhand + sixthhand + seventhhand
        if HitOrStand in ["stand"]:
          stand()
        HitOrStand = input(f"Type \"hit\" To Hit And \"stand\" To Stand \n Dealer is Showing {A1A}")
        if HitOrStand in ["hit"]:
          RandomNumber = random.randint(0, 12)
          fourthhand = card_deck[RandomNumber]
          print(f"Your Hand: {firsthand}, {secondhand}, {thirdhand}, {fourthhand} Total: {firsthand + secondhand + thirdhand + fourthhand}")
          bust()
          FourthPull = True
          ThirdPull = False
      while FourthPull:
        if HitOrStand in ["stand"]:
          stand()
        HitOrStand = input(f"Type \"hit\" To Hit And \"stand\" To Stand \n Dealer is Showing {A1A}")
        if HitOrStand in ["hit"]:
          RandomNumber = random.randint(0, 12)
          fifthhand = card_deck[RandomNumber]
          print(f"Your Hand: {firsthand}, {secondhand}, {thirdhand}, {fourthhand}, {fifthhand} Total: {firsthand + secondhand + thirdhand + fourthhand + fifthhand}")
          bust()
          FourthPull = False
          FifthPull = True
          bust()
      while FifthPull:
        if HitOrStand in ["stand"]:
          stand()
        HitOrStand = input(f"Type \"hit\" To Hit And \"stand\" To Stand \n Dealer is Showing {A1A}")
        if HitOrStand in ["hit"]:
          RandomNumber = random.randint(0, 12)
          sixthhand = card_deck[RandomNumber]
          print(f"Your Hand: {firsthand}, {secondhand}, {thirdhand}, {fourthhand}, {fifthhand}, {sixthhand} Total: {firsthand + secondhand + thirdhand + fourthhand + fifthhand + sixthhand}")
          bust()
          FifthPull = False
          SixthPull = True
          bust()
      while SixthPull:
        if HitOrStand in ["stand"]:
          stand()
        HitOrStand = input(f"Type \"hit\" To Hit And \"stand\" To Stand \n Dealer is Showing {A1A}")
        if HitOrStand in ["hit"]:
          RandomNumber = random.randint(0, 12)
          seventhhand = card_deck[RandomNumber]
          print(f"Your Hand: {firsthand}, {secondhand}, {thirdhand}, {fourthhand}, {fifthhand}, {sixthhand}, {seventhhand} Total: {firsthand + secondhand + thirdhand + fourthhand + fifthhand + sixthhand + seventhhand}")
          bust()
          SixthPull = False
          SeventhPull = True
          bust()
      while SeventhPull:
        if HitOrStand in ["stand"]:
          stand()
        print(s)
        SeventhPull = False

  def roll():
    money = 50000
    bet = int(input("Enter The Amout of Money You Can lose: ")) 
    while (money < bet):
      print("You Only Have:", money)
      bet = int(input("Bet: ")) 
    tar = int(input("Choose a Target: "))
    coc = input("Choose Over or Under: ")
    while (coc != "over") and (coc != "under"):
      coc = input("PLEASE CHOOSE EITHER \"over\" OR \"under\": ")
    multiplier = 0 
    risk = 0
    replay = ""
    while (money > 0):
      money = money - bet
      dice = random.randint(1,100)
      print("Rollin'...")
      time.sleep(0.910)
      print("ROLLED:", dice)
      if coc in ["over"]:
          risk = 100 - tar
      if coc in ["under"]:
          risk = tar - 1
      risk = risk / 100
      multiplier = round(0.98 / risk, 2)
      if (coc == "over"):
        if (tar < dice):
          money = round(money + bet * multiplier,)
          print(f"----YOU WON---- {money} With {multiplier}x Multiplier!")
          print("")
        else:
          print(f"------YOU LOST------ you lost {bet} dollars and have {money} left")
          print("")
      if (coc == "under"):
        if (tar > dice):
          money = round(money + bet * multiplier,)
          print(f"----YOU WON---- {money} With {multiplier}x Multiplier!")
          print("")
        else:
          print(f"------YOU LOST------ you lost {bet} dollars and have {money} left")
          print("")
      if (money < 0):
          print("YOU LOST ALL OF IT AND YOU ARE NOW IN DEBT!")
      elif (money == 0):
          print("YOU LOST ALL OF IT!")
      if (money > 0):
        replay = input("Press Anything To Play Again")

  def gg(): # GUESSING GAME FOR THOSE WHO ARE READING ALSO 67
    while True:
      guess = 0
      money = 50000
      again = ""
      multiplier = 36.67
      bet = int(input("Enter The Amout of Money You Can lose: "))
      while (money < bet):
        print("You Only Have:", money)
        bet = int(input('Enter Bet'))
      lives = 6
      rn = random.randint(1, 100) 
      guess = int(input(f"Guess a Number Between 1 and 100!: "))
      win = False
      while (lives > 0) and not win:
        if guess < rn:
          multiplier = round(multiplier / 2, 2)
          print("Lives Left:", lives)
          print(f"Current multiplier: {multiplier}")
          guess = int(input("Guess Higher!: "))
          lives -= 1
        elif guess > rn:
          multiplier = round(multiplier / 2, 2)
          print("Lives Left:", lives)
          print(f"Current multiplier: {multiplier}")
          guess = int(input("Guess Lower!: "))
          lives -= 1
        else:
          money += round(bet * multiplier, 0)
          print(f"You Win! YOU WON {bet * multiplier} WITH {multiplier}x Your bet!")
          win = True
        if lives == 0:
          money -= bet
          print("You Lost!")
          print(f"The Number Was: {rn}")
          print(f"YOU HAVE {money} now! ")
          again = 67
      if money <= 0:
        print("You Are Broke!")
      again = input("Press Anything To Play Again!")
      win = False

  repeat = True
  while repeat:
    GameChoice = input(f"Enter a Command To Play!\n /roll: roll gambling game\n /blackjack: blackjack gambling game\n /guessing_game: gambling guessing game \n /help: provides help with all gamemodes")
    repeat = False
    if (GameChoice == "/roll"):
      roll()
    elif (GameChoice == "/blackjack"):
      blackjack()
    elif (GameChoice == "/guessing_game"):
      gg()
    elif (GameChoice == "/help"):
      print("roll: a roll dice game, the dice has 100 sides, you will pick a target (3-97) and a choice (over, under), if the dice rolled over your target (and you have chosen \"over\") you will win, else you will lose, so if you were to go target 50, and use over, the dice will roll, and if it rolled above 50, you will win, below that (or equal) will result in a loss, keep in mind that the prize multiplier will vary depending on tne risk you took. \n blackjack: blackjack is a gamemode that you try to beat the Dealer in, the person (you or the dealer) who gets closer to 21 without going over it wins, if you went above 21 the dealer will automatically win, if you were closer to 21 than the dealer you win, so when you have a lower hand (0-11) you should hit (draw card (you can stand if you want)) and if you had Anything above or equal 17 you should stand, google this game for better explanation. \n guessing game is a game where you gamble money as well, you guess a number Between one and one hundred, the more guesses it takes you to find the number Between 1 and 100 you have several guesses untill you lose yojr money, if you win, your multiplier depends on how many guesses you have left, first guess will give you 36x and then it gets devided by two each guess. \n \n \n")
      repeat = True
    else:
      print("Command not found.")
      repeat = True