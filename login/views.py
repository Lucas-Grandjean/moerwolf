from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from login.models import Card
from accounts.models import User


# Create your views here.
def home(request):
    return render(request, 'login/index.html')

def signin(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['pwd']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            uname = user.username
            return render(request, "login/index.html")
        else:
            messages.error(request, "Incorrect !")
            return redirect("home")
    return render(request, 'login/connexion.html')

def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['pwd']
        password_confirm = request.POST['pwdconfirm']

        if User.objects.filter(username=username):
            messages.error(request, 'Le nom d\'utilisateur est déjà pris')
            return redirect('home')
        
        if password != password_confirm:
            messages.error(request, 'La confirmation du mot de passe est invalide')
            return redirect('home')    

        if not username.isalnum():
            messages.error(request, 'Le pseudo doit être alphanumérique')
            return redirect('home')                        

        new_user = User.objects.create_user(username, password)
        new_user.save()

        messages.success(request, 'Votre compte a été crée avec succès')
        return redirect("home")


    return render(request, 'login/inscription.html')

def signout(request):
    logout(request)
    messages.success(request, 'Deconnexion faites avec succes')
    return redirect('home')

def rules(request):
    return render(request, 'login/regles.html')

def cardlist(request):
    all_cards = Card.objects.all()
    context={
    'all_cards':all_cards
    }
    return render(request,'login/listecartes.html', context)