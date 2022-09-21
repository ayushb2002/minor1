from datetime import datetime
from django.shortcuts import render, redirect
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from .models import Learner, DailyChallenge, TrackDailyChallenge, UserPersonalDetails
import pandas as pd
import os
import random

database = pd.read_csv("home/database/dictionary.csv")


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


def generateOptions():
    n = len(database)
    optNo = random.sample(range(0, n-1), 2)
    meaning1 = database['def'][optNo[0]]
    meaning2 = database['def'][optNo[1]]
    return [meaning1, meaning2]


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
            personalDetails = UserPersonalDetails.objects.create(user=request.user)
            personalDetails.save()
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
    context = {"name": request.user.first_name +
               ' '+request.user.last_name, "loggedIn": True}
    return render(request, "welcome.html", context)


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
def dailyChallenge(request):
    if request.method == "POST":
        selected = request.POST['option']
        context = {
            "name": request.user.first_name+' '+request.user.last_name,
            "loggedIn": True,
        }
        try:
            daily = DailyChallenge.objects.filter(
                date=datetime.today().strftime('%Y-%m-%d'))
            dc = daily.values()
            if selected == dc[0]['meaning']:
                context['submit'] = True
                context['success'] = True
                context['message'] = "Your answer is right! Come back tomorrow for next challenge!"
                track = TrackDailyChallenge.objects.create(user=request.user, challenge=daily[0], solvedCorrectly=True)
                track.save()
                return render(request, "dailyChallenge.html", context)
            else:
                context['submit'] = True
                context['success'] = False
                context['message'] = "You answer is wrong! The right meaning of the word is " + \
                    dc[0]['meaning']+". See you tomorrow!"
                track = TrackDailyChallenge.objects.create(user=request.user, challenge=daily[0])
                track.save()
                return render(request, "dailyChallenge.html", context)
        except:
            context['message'] = "Could not submit the answer!"
            return render(request, "dailyChallenge.html", context)
    else:
        try:
            track = TrackDailyChallenge.objects.filter(
                user=request.user, date=datetime.today().strftime('%Y-%m-%d')).values()
            if track:
                return render(request, "dailyChallenge.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "message": "You have already solved today's challenge, come back tomorrow for new one!"})
            else:
                try:
                    dc = DailyChallenge.objects.filter(
                        date=datetime.today().strftime('%Y-%m-%d')).values()
                    options = generateOptions()
                    options.append(dc[0]['meaning'])
                    random.shuffle(options)
                    word = dc[0]['word']
                    return render(request, "dailyChallenge.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "word": word, "meaning": options, "date": dc[0]['date']})
                except:
                    return render(request, "dailyChallenge.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "message": "Today's daily challenge will be uploaded soon!"})
        except:
            return render(request, "dailyChallenge.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "message": "Server error! Try again later!"})
        


@login_required
def addDailyChallenge(request):
    if request.user.is_superuser:
        dc = DailyChallenge.objects.filter(
            date=datetime.today().strftime('%Y-%m-%d'))
        if dc:
            return render(request, "welcome.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "message": "Today's word has been already added!"})
        else:
            return render(request, "addDailyChallenge.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True})
    else:
        return redirect('settings')


@login_required
def addedDailyChallenge(request):
    if request.user.is_superuser and request.method == "POST":
        word = request.POST['word']
        meaning = request.POST['meaning']
        try:
            dailyChallenge = DailyChallenge.objects.create(
                word=word, meaning=meaning)
            dailyChallenge.save()
        except:
            return render(request, "welcome.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "message": "Could not add new word!"})

        return render(request, "welcome.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "message": "Word Successfully added!"})
    elif request.method != "POST":
        return HttpResponseNotFound('<h1>Bad request</h1>')
    else:
        return redirect('settings')


@login_required
def updateLearner(request):
    if request.method == "POST":
        level = request.POST['level']
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

@login_required
def track(request):
    try:
        track = TrackDailyChallenge.objects.filter(user=request.user)
        if track:
            return render(request, "track.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "record": reversed(track), "total": len(track)})
        else:
            return render(request, "track.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "message": "No challenge played yet!"})
    except:
        return render(request, "track.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "message": "Server error! Try again later!"})

@login_required
def userPersonalDetails(request):
    if request.method == "POST":
        age_group = request.POST['age']
        education_group = request.POST['education']
        try:
            personalDetails = UserPersonalDetails.objects.filter(
                user=request.user).update(age_group=age_group, education_group=education_group)
        except:
            personalDetails = UserPersonalDetails.objects.create(age_group=age_group, education_group=education_group, user=request.user)
            personalDetails.save()
            return render(request, "ageAndEducation.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "message": "Created new preference!"})

        return render(request, "ageAndEducation.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "message": "Updated previous preference!"})
    else:
        try:
            personalDetails = UserPersonalDetails.objects.filter(user=request.user).values()
        except:
            return HttpResponseNotFound('<h1>Error in user profile!</h1>')

        return render(request, "ageAndEducation.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "details": personalDetails[0]})