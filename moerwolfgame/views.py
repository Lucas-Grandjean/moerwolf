from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from moerwolfgame.models import Game, Message
from accounts.models import User

def chat(request, urlgameid):
    try:
        message_logs = Message.objects.filter(game = request.user.ongoing_game, state_visible = 1 ) | Message.objects.filter(game = request.user.ongoing_game, state_visible = 3, side = request.user.player_card.side) | Message.objects.filter(game = request.user.ongoing_game, state_visible = 2, owner = request.user)
    except:
        message_logs = None    
    context={
    'urlgameid':urlgameid,
    'message_logs':message_logs,
    'redirect':0
    }
    if (request.user.ongoing_game and request.user.ongoing_game.id == urlgameid):
        return render(request,'moerwolfgame/chat.html', context)
    else:
        return render(request,'moerwolfgame/chat.html', {'redirect':1})


def actions(request, urlgameid, urlgamerole):
    try: # Si on a aucune info de la game, on redirect au lobby
        game_infos = Game.objects.get(id = urlgameid)
    except:
        return redirect("jouer/lobby")

    try:
        party_players = User.objects.filter(ongoing_game = request.user.ongoing_game)
    except:
        return redirect("jouer/lobby")

    context={
    'game_infos':game_infos,
    'party_players':party_players,
    'urlgamerole':urlgamerole
    }
    templateurl = 'moerwolfgame/actions' + str(urlgamerole) + '.html' 
    if (request.user.ongoing_game and request.user.player_card and request.user.player_card.id == urlgamerole):
        return render(request,templateurl, context)
    else:
        return redirect("jouer/lobby")


def game(request, urlgameid):

    # On lance si l'admin a voulu
    if request.method =='POST':
        #### LANCER PARTIE ####
        if(request.POST.get('launchgameadmin') is not None):
            if request.user.is_staff:
                request.user.ongoing_game.launch()
        #### VOTE VILLAGEOIS ####
        elif(request.POST.get('vote') is not None):
            if request.user.has_voted == False: # Si l'user n'a pas voté
                if request.user.ongoing_game.id == urlgameid: #Si l'user est bien dans la bonne game
                    if request.user.ongoing_game.dayState == 1: #Si c'est le jour
                        if request.user.alive == True: #Si l'user est en vie
                            if request.user.ongoing_game.voting_available == True: #Si le vote est possible
                                request.user.ongoing_game.vote(request.POST['vote'], request.user)
        #### VOTE LOUP ####
        elif(request.POST.get('votewolf') is not None):
            if request.user.has_voted == False: # Si l'user n'a pas voté
                if request.user.ongoing_game.id == urlgameid: #Si l'user est bien dans la bonne game
                    if request.user.ongoing_game.dayState == 2: #Si c'est la nuit
                        if request.user.alive == True: #Si l'user est en vie
                            if request.user.ongoing_game.voting_available == True: #Si le vote est possible
                                if request.user.player_card.side == 'EVIL': #Si le joueur est méchant
                                    request.user.ongoing_game.wolf_vote(request.POST['votewolf'], request.user)
        #### POUVOIR SEER ####
        elif(request.POST.get('seer') is not None):
            if request.user.power_usage == 1:
                if request.user.ongoing_game.id == urlgameid: #Si l'user est bien dans la bonne game
                    if request.user.ongoing_game.dayState == 2: #Si c'est la nuit
                        if request.user.alive == True: #Si l'user est en vie
                                if request.user.player_card.id == 3: #Si le joueur est SEER
                                    request.user.ongoing_game.seer_power(request.POST['seer'], request.user)            
        #### POUVOIR GUARD ####
        elif(request.POST.get('guard') is not None):
            if request.user.power_usage == 1:
                if request.user.ongoing_game.id == urlgameid: #Si l'user est bien dans la bonne game
                    if request.user.ongoing_game.dayState == 2: #Si c'est la nuit
                        if request.user.alive == True: #Si l'user est en vie
                                if request.user.player_card.id == 5: #Si le joueur est GUARD
                                    request.user.ongoing_game.guard_power(request.POST['guard'], request.user)
        #### POUVOIR WITCH (KILL) ####
        elif(request.POST.get('killpotion') is not None):
            if request.user.power_usage == 1 or request.user.power_usage == 3:
                if request.user.ongoing_game.id == urlgameid: #Si l'user est bien dans la bonne game
                    if request.user.ongoing_game.dayState == 2: #Si c'est la nuit
                        if request.user.alive == True: #Si l'user est en vie
                                if request.user.player_card.id == 6: #Si le joueur est WITCH
                                    if request.user.has_voted == False: # Debug 2 popo 1 nuit
                                        request.user.ongoing_game.kill_potion(request.POST['killpotion'], request.user)   
        #### POUVOIR WITCH (HEAL) ####
        elif(request.POST.get('healpotion') is not None):
            if request.user.power_usage == 1 or request.user.power_usage == 4:
                if request.user.ongoing_game.id == urlgameid: #Si l'user est bien dans la bonne game
                    if request.user.ongoing_game.dayState == 2: #Si c'est la nuit
                        if request.user.alive == True: #Si l'user est en vie
                                if request.user.player_card.id == 6: #Si le joueur est WITCH
                                    if request.user.has_voted == False: # Debug 2 popo 1 nuit
                                        request.user.ongoing_game.heal_potion(request.POST['healpotion'], request.user)   
        #### POUVOIR HUNTER ####
        elif(request.POST.get('shoot') is not None):
            if request.user.power_usage == 1:
                if request.user.ongoing_game.id == urlgameid: #Si l'user est bien dans la bonne game
                    if request.user.ongoing_game.dayState == 1: #Si c'est le jour
                        if request.user.alive == False: #Si l'user est mort
                                if request.user.player_card.id == 7: #Si le joueur est HUNTER
                                    request.user.ongoing_game.shoot(request.POST['shoot'], request.user)   
        #### PAS DE POST VALIDE ####
        else:
            print('R En POST de valide')

    # On cherche les messages liés à la partie et on les transmet au contexte
    try:
        message_logs = Message.objects.filter(game = request.user.ongoing_game, state_visible = 1 ) | Message.objects.filter(game = request.user.ongoing_game, state_visible = 3, side = request.user.player_card.side) | Message.objects.filter(game = request.user.ongoing_game, state_visible = 2, owner = request.user)
    except:
        message_logs = None

    try: # Si on a aucune info de la game, on redirect au lobby
        game_infos = Game.objects.get(id = urlgameid)
    except:
        return redirect("jouer/lobby")

    party_players = User.objects.filter(ongoing_game = request.user.ongoing_game)

    # Urlgamerole = Check l'ID du role du joueur afin de chercher son rolebox
    if(request.user.player_card):
        urlgamerole = request.user.player_card.id
    else:
        urlgamerole = 2

    context={
    'urlgameid':urlgameid,
    'message_logs':message_logs,
    'party_players':party_players,
    'game_infos':game_infos,
    'urlgamerole':urlgamerole
    }
    if (request.user.ongoing_game.id == urlgameid):
        return render(request,'moerwolfgame/game.html', context)
    else:
        return redirect("jouer/lobby")

# Create your views here.
def lobby(request):

    if request.method =='POST':
        # Check si c'est une game que l'on veut rejoindre
        if(request.POST.get('gameID') is not None):
            game_joined = Game.objects.get(id=request.POST.get('gameID'))
            if(request.user.ongoing_game is None):
                if(game_joined.currentplayers < game_joined.maxplayers):
                    if(game_joined.state == 1):
                        current_user = request.user
                        current_user.ongoing_game = game_joined
                        current_user.save()
                        print('User ', current_user.username , ' set to game ', str(game_joined))
                        game_joined.currentplayers = game_joined.currentplayers + 1
                        game_joined.save()
                    else:
                        print('Erreur : Partie terminée ou en cours')
                else:
                    print('Erreur : Partie pleine')
            else:
                print('Erreur : Joueur déjà en partie')
        elif(request.POST.get('gobackp') is not None):
            if(request.user.ongoing_game is not None):
                placeredir = "game/" + str(request.user.ongoing_game.id)
                return redirect(placeredir)
            else:
                print('Erreur : Joueur pas en partie')                     
        elif(request.POST.get('leavep') is not None):
            if(request.user.ongoing_game is not None):
                current_user = request.user
                current_user.ongoing_game.currentplayers = current_user.ongoing_game.currentplayers - 1
                current_user.ongoing_game.save()
                current_user.ongoing_game = None
                current_user.save()
            else:
                print('Erreur : Joueur pas en partie')            
        elif(request.POST.get('gamestart') is not None):
            new_game = Game()
            new_game.save()
        else:
            print('ERREUR POST')

    all_games = Game.objects.filter(state = 1) | Game.objects.filter(state = 2)
    if(request.user.ongoing_game is not None):
        party_players = User.objects.filter(ongoing_game = request.user.ongoing_game)
        print(party_players)
    else:
        party_players = None

    context={
    'all_games':all_games,
    'party_players':party_players,
    }
    return render(request,'moerwolfgame/lobby.html', context)