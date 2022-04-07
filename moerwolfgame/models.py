from django.db import models
from login.models import Card
from accounts.models import User
from django.utils import timezone
import time # sleep
import datetime

class Message(models.Model):

    # 1 = Visible à tous
    # 3 = Visible par un clan (EVIL, GOOD, NEUTRAL)
    # 2 = Visible par l'owner
    # 4 = Visible par un Modérateur / Staff
    content = models.TextField(default='VIDE')
    date = models.DateTimeField(auto_now_add=True, blank=True)
    color = models.CharField(default='white', max_length=10)
    state_visible = models.IntegerField(default=0)
    side = models.CharField(default='ALL', max_length=10)
    owner = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    game = models.ForeignKey(
        "moerwolfgame.Game",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ['date']

    def __str__(self):
        return self.content

    def timed(self):
        return self.date.strftime('%H:%M')

class Game(models.Model):


    maxplayers = models.IntegerField(default=2) # Nb max joueurs
    state = models.IntegerField(default=1) # (0 (Finished) // 1 (Join) // 2 (Launched))
    currentplayers = models.IntegerField(default=0) # Nb players actuels en game
    dayState = models.IntegerField(default=0) # 0(DEBUG STATE) // 1(JOUR) // 2(NUIT)
    dayNumber = models.IntegerField(default=0) # Numéro de la journée
    voting_available = models.BooleanField(default=True) # Si on peut voter (désactivé pour des events tel que chasseur)


    class Meta:
        ordering = ['maxplayers']

    def __str__(self):
        return 'Partie ' + str(self.id)

    # @shoot : Permet à l'Hunter de tirer
    def shoot(self, target, user):
        target_p = User.objects.get(username = target)
        self.kill(target_p)
        message_content = 'Le chasseur a abattu ' + target_p.username + ' !'
        new_message = Message.objects.create(content=message_content, color='blue', state_visible=1, game=self)
        new_message.save()
        user.power_usage = 0
        user.save()

    # @seer_power : Permet d'utiliser le pouvoir de voyance
    def seer_power(self, target, user):
        target_p = User.objects.get(username = target)
        side_message = ''
        if(target_p.player_card and target_p.player_card.side == 'EVIL'):
            side_message = 'méchant'
        elif(target_p.player_card and target_p.player_card.side == 'EVIL'):
            side_message = 'gentil'
        else:
            side_message = 'neutre'
        message_content = 'Grâce à vos pouvoirs psychiques, vous pensez que ' + target_p.username + ' est ' + side_message + ' !'
        new_message = Message.objects.create(content=message_content, color='silver', state_visible=2, owner=user, game=self)
        new_message.save()
        user.power_usage = 2
        user.save()     

   # @guard_power : Permet d'utiliser le pouvoir de garde
    def guard_power(self, target, user):
        target_p = User.objects.get(username = target)
        message_content = 'Vous décidez de protéger ' + target_p.username + ' ce soir.'
        new_message = Message.objects.create(content=message_content, color='silver', state_visible=2, owner=user, game=self)
        new_message.save()
        if(target_p == user):
            user.guarded = True
        else:
            target_p.guarded = True
            target_p.save()
        user.power_usage = 2
        user.save()  

  # @heal_potion : Permet d'utiliser la potion de heal (WITCH)
    def heal_potion(self, target, user):
        target_p = User.objects.get(username = target)
        message_content = 'Vous décidez de soigner ' + target_p.username + ' avec votre potion.'
        new_message = Message.objects.create(content=message_content, color='silver', state_visible=2, owner=user, game=self)
        new_message.save()
        if(target_p == user):
            user.healed = True
        else:
            target_p.healed = True
            target_p.save()
        if(user.power_usage == 1) : user.power_usage = 3
        elif(user.power_usage == 4) : user.power_usage = 0
        user.has_voted = True # Pour empêcher la sorcière d'utiliser ses 2 popo en 1 nuit
        user.save()  

  # @kill_potion : Permet d'utiliser la potion de kill (WITCH)
    def kill_potion(self, target, user):
        target_p = User.objects.get(username = target)
        message_content = 'Vous décidez de tuer ' + target_p.username + ' avec votre potion.'
        new_message = Message.objects.create(content=message_content, color='silver', state_visible=2, owner=user, game=self)
        new_message.save()
        if(target_p == user):
            user.death_potion = True
        else:
            target_p.death_potion = True
            target_p.save()
        if(user.power_usage == 1) : user.power_usage = 4
        elif(user.power_usage == 3) : user.power_usage = 0
        user.has_voted = True # Pour empêcher la sorcière d'utiliser ses 2 popo en 1 nuit
        user.save()  

    # @reset_votes : Remet le compteur de votes à 0 (Villageois & Loups) (+ Power)
    def reset_votes(self):
        hunter_can_shoot = False
        all_users = User.objects.filter(ongoing_game = self)
        for user in all_users:
            user.has_voted = False
            user.votes = 0
            user.wolf_votes = 0
            if(not user.alive and user.power_usage == 1 and user.player_card.id == 7) : hunter_can_shoot = user
            if(user.power_usage == 2) : user.power_usage = 1
            if user.guarded : user.guarded = False
            if user.healed : user.healed = False
            if user.death_potion :
                user.death_potion = False
                user.save()
                if(self.kill(user)):
                    message_content = user.username + ' a été tué par une potion ! Il était ' + user.player_card.name + '.'
                    new_message = Message.objects.create(content=message_content, color='blue', state_visible=1, game=self)
                    new_message.save()             
            user.save()
        self.save()
        return hunter_can_shoot

    # @reset_stats : Remet les stats à 0
    def reset_stats(self):
        all_users = User.objects.filter(ongoing_game = self)
        for user in all_users:
            user.alive = False
            user.ongoing_game = None
            user.player_card = None
            user.power_usage = 0
            user.save()
        all_users.save()

    # @close_votes : Ferme les votes et elimine le joueur voté s'il la majorité des votes
    def close_votes(self):
        all_users = User.objects.filter(ongoing_game = self, alive = True)
        for user in all_users:
            print('Debug I : On cherche si ', user, ' a plus de votes que la moitié (', str(user.votes), ' / ', str(len(all_users)/2), ' )' )
            if(user.votes > len(all_users)/2 ): #Si + de la moitié des votes on le tue
                if(user.player_card.id == 8 and user.power_usage == 1):
                    message_content = user.username + ' a survécu au vote grâce à son role de ' + user.player_card.name + ' !'
                    new_message = Message.objects.create(content=message_content, color='gray', state_visible=1, game=self)
                    new_message.save()
                    user.power_usage = 0
                    user.save() 
                else:               
                    print('Debug I : On tue ', user)
                    message_content = user.username + ' a été voté ! Il était ' + user.player_card.name + '.'
                    new_message = Message.objects.create(content=message_content, color='blue', state_visible=1, game=self)
                    new_message.save()
                    self.kill(user)
            user.votes = 0
            user.save()

    # @close_votes_wolf : Ferme les votes des loups et elimine le joueur voté s'il a tout les votes
    def close_votes_wolf(self):
        most_voted_user = User.objects.filter(ongoing_game = self, alive = True).order_by('-wolf_votes')[0]
        if(most_voted_user.wolf_votes >= 1):
            if(self.kill(most_voted_user)):
                message_content = most_voted_user.username + ' a été dévoré ! Il était ' + most_voted_user.player_card.name + '.'
                new_message = Message.objects.create(content=message_content, color='blue', state_visible=1, game=self)
                new_message.save()
    
    # @check_win_condition : Analyse si la game est terminée (0 : Non, 1 : Victoire GOOD, 2 : Victoire EVIL)
    def check_win_condition(self):
        # On établit le camp des survivants
        good_left = bad_left = neutral_left = 0
        user_left = User.objects.filter(ongoing_game = self, alive = True)
        for user in user_left:
            if user.player_card.side == 'GOOD':
                good_left += 10
            elif user.player_card.side == 'EVIL':
                bad_left += 1
            else:
                neutral_left += 1

        if(good_left + bad_left == 0):
            self.end_game(3)
        elif(bad_left >= 1 and good_left <= 1 ):
            self.end_game(2)
        elif(bad_left == 0):
            self.end_game(1)
        else:
            return 0

    # @end_game : Termine la game
    def end_game(self, win_side):
        if(win_side == 1):
            message_content = 'Victoire du village !'
            message_color = 'green'
        elif(win_side == 2):
            message_content = 'Victoire des loups!'
            message_color = 'red'
        else:
            message_content = 'Egalité !'
            message_color = 'gray'

        new_message = Message.objects.create(content=message_content, color=message_color, state_visible=1, game=self)
        new_message.save()   

        new_message = Message.objects.create(content='Fermeture de la partie dans 10 secondes...', color='lightblue', state_visible=1, game=self)
        new_message.save()   

        time.sleep(10) 

        # Supression des messages
        Message.objects.filter(game = self).delete()

        # Reset les stats des joueurs
        self.state = 0
        self.save()
        self.reset_votes()
        self.reset_stats()
        self.save()

    # @kill : Permet d'éliminer un joueur
    def kill(self, user):
        if(user.guarded):
            new_message = Message.objects.create(content='Un joueur a été sauvé par le garde cette nuit !', color='green', state_visible=1, game=self)
            new_message.save()
            return False
        elif(user.healed):
            new_message = Message.objects.create(content='Un joueur a été sauvé par une potion de soin cette nuit !', color='green', state_visible=1, game=self)
            new_message.save()
            return False
        else:     
            user.alive = False
            user.save()
            return True

    # @set_night : Met la nuit dans la partie
    def set_night(self):
        new_message = Message.objects.create(content='La nuit va bientôt tomber dans le village...', color='gray', state_visible=1, game=self)
        new_message.save()
        time.sleep(5)
        new_message = Message.objects.create(content='La nuit tombe dans le village. Bonne nuit !', color='purple', state_visible=1, game=self)
        new_message.save()
        self.dayState = 2
        self.reset_votes()
        self.save()
        new_message = Message.objects.create(content='Il est temps pour vous de choisir qui manger.', color='red', state_visible=3, game=self, side='EVIL')
        new_message.save()
        time.sleep(10)
        self.set_day()

    # @set_day : Met le jour dans la partie
    def set_day(self):
        new_message = Message.objects.create(content='Le jour arrive bientôt au village...', color='gray', state_visible=1, game=self)
        new_message.save()
        time.sleep(5)
        new_message = Message.objects.create(content='Le soleil se lève dans le village. Bon réveil !', color='green', state_visible=1, game=self)
        new_message.save()
        self.close_votes_wolf()
        hunter = self.reset_votes() # Reset les votes & stats, j'en profite pour vérifier si un hunter est mort
        if(hunter): # Si un hunter est mort
            print('Hunter')
            new_message = Message.objects.create(content='Le chasseur possède 10 secondes pour abattre sa cible !', color='gray', state_visible=1, game=self)
            new_message.save()
            self.dayState = 1 # Set le jour
            self.voting_available = False
            self.save()
            time.sleep(10)
            hunter.power_usage = 0
            self.voting_available = True
            self.save()
        else:
            print('Pas hunter !')
            self.dayState = 1 # Set le jour
            self.save()        
        if(not self.check_win_condition()):
            time.sleep(10)
            new_message = Message.objects.create(content='La journée semble bientôt se terminer', color='gray', state_visible=1, game=self)
            new_message.save()
            time.sleep(10)
            new_message = Message.objects.create(content='La journée est terminée !', color='gray', state_visible=1, game=self)
            new_message.save()
            self.close_votes()
            if(not self.check_win_condition()):
                time.sleep(5)
                self.set_night()

    # @launch : Lance la partie
    def launch(self):
        import random
        self.state = 2
        self.save()
        list_players = User.objects.filter(ongoing_game = self)

        #DEAL LES CARTES
        available_cards = []

        print('Debug I : On deal les cartes')

        # On prends un evil et on l'ajoute au pif, 2 si >+ 5
        bad_roles = Card.objects.filter(side = 'EVIL')
        available_cards.append(bad_roles.order_by('?')[0])
        if(len(list_players) >= 5): 
            bad_roles = Card.objects.filter(side = 'EVIL')
            available_cards.append(bad_roles.order_by('?')[0])
        # On comble avec les gentils (TODO neutral)
        i = 0
        print('DEBUG NB NEEDED : ', str((len(list_players) - len(available_cards))))
        while i < ((len(list_players) - len(available_cards)) ):
            if(i < (len(list_players) - len(available_cards)) ):
                #specific_card = Card.objects.filter(side = 'GOOD').order_by('?')[0]
                specific_card = Card.objects.filter(side = 'GOOD', id=8)[0]
                if specific_card.unique == True and specific_card in available_cards:
                    print('Debug EI : Role unique, on reroll')
                else:
                    available_cards.append(specific_card)
                    i += 1
                    print('Debug I : Carte tradée : ', str(specific_card))
            else:
                print('Debug E : Trop de rolls')
        print('Debug I : Rolls terminés')



        random.shuffle(available_cards)

        # On associe les cartes aux joueurs
        for player in list_players:

            # Set les stats des joueurs
            player.alive = True
            player.has_voted = False
            player.vote = 0
            player.power_usage = 1
            player.player_card = available_cards[0]
            available_cards.pop(0)
            player.save()

        print('Debug I : Partie lancée')
        
        new_message = Message.objects.create(content='La partie est lancée !', color='gray', state_visible=1, game=self)
        new_message.save()

        self.set_night()
        self.save()

    # @vote : Gère le vote 
    def vote(self, target, user):
        target_vote = User.objects.get(username = target)
        if(user.player_card.id == 4): # Vote double pour maire
            target_vote.votes = target_vote.votes + 2
        else:
            target_vote.votes = target_vote.votes + 1
        if(target_vote == user): #Antibug pour le vote contre soi-même
            target_vote.has_voted = True
        else:
            user.has_voted = True
            user.save()
        target_vote.save()
        message_content = user.username + ' a voté pour ' + target_vote.username + ' ! ( ' + str(target_vote.votes) + ' )'
        new_message = Message.objects.create(content=message_content, color='green', state_visible=1, game=self)
        new_message.save()

    # @wolf_vote : Gère le vote des loups
    def wolf_vote(self, target, user):
        target_vote = User.objects.get(username = target)
        target_vote.wolf_votes = target_vote.wolf_votes + 1
        if(target_vote == user): #Antibug pour le vote contre soi-même
            target_vote.has_voted = True
            target_vote.save()
        else:
            user.has_voted = True
            user.save()
        target_vote.save()
        message_content = user.username + ' a voté pour manger ' + target_vote.username + ' ! '
        new_message = Message.objects.create(content=message_content, color='red', state_visible=3, side='EVIL', game=self)
        new_message.save()