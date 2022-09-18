from django.shortcuts import render, redirect
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from .models import Learner


def index(request):
    if request.user.is_authenticated:
        return render(request, "index.html", {"loggedIn": True})

    else:
        return render(request, "index.html", {"loggedIn": False})


def learn(request):
    if request.user.is_authenticated:
        return render(request, "learn.html", {"loggedIn": True})

    else:
        return render(request, "learn.html", {"loggedIn": False})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('settings')

    else:
        return render(request, "login.html", {"loggedIn": False})


def register(request):
    if request.user.is_authenticated:
        return redirect('settings')

    else:
        return render(request, "register.html", {"loggedIn": False})


def signup(request):
    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST['lname']
        uname = request.POST['uname']
        email = request.POST['registerEmail']
        pwd = request.POST['registerPwd']

        try:
            user = User.objects.create_user(uname, email, pwd)
            user.first_name = fname
            user.last_name = lname
            user.save()
            learner = Learner.objects.create(level='BEG', user=user)
            learner.save()
        except:
            return render(request, "register.html", {"message": "Cannot create the user!", "loggedIn": False})

        return render(request, "login.html", {"message": "User created successfully!", "loggedIn": False})
    else:
        return HttpResponseNotFound('<h1>Bad request!</h1>')


def signin(request):
    if request.method == "POST":
        uname = request.POST['uname']
        pwd = request.POST['registerPwd']
        user = authenticate(request, username=uname, password=pwd)
        if user is not None:
            login(request, user)
            return redirect('settings')
        else:
            return render(request, "login.html", {"message": "Invalid credentials!", "loggedIn": False})
    else:
        return HttpResponseNotFound('<h1>Bad request!</h1>')


@login_required
def logout_view(request):
    logout(request)
    return render(request, "login.html", {"message": "Logged out!", "loggedIn": False})


def loggedInView(request):
    return render(request, "welcome.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True})


@login_required
def editSettings(request):
    return render(request, "editSettings.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True})


@login_required
def changePassword(request):
    return render(request, "changePassword.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True})


@login_required
def deleteAccount(request):
    return render(request, "deleteAccount.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True})


@login_required
def updateLearner(request):
    if request.method == "POST":
        level = request.POST['level']
        print(level)
        try:
            learner = Learner.objects.filter(
                user=request.user).update(level=level)
        except:
            learner = Learner.objects.create(level=level, user=request.user)
            learner.save()
            return render(request, "welcome.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "message": "Created new preference!"})

        return render(request, "welcome.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "message": "Updated previous preference!"})
    else:
        return HttpResponseNotFound('<h1>Bad request!</h1>')
