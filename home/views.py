from datetime import datetime
import datetime as dtm
from django.shortcuts import render, redirect
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from .models import Learner, DailyChallenge, TrackDailyChallenge, UserPersonalDetails, TrackLeaderboard, DailyLearner
import pandas as pd
import numpy as np
import random
from pytz import timezone
import requests

API_TOKEN = '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'
API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

database = pd.read_csv("home/database/dictionary.csv")

def generateOptions():
    n = len(database)
    optNo = random.sample(range(0, n-1), 2)
    meaning1 = database['def'][optNo[0]]
    meaning2 = database['def'][optNo[1]]
    return [meaning1, meaning2]

def determineLevel(age_group, education_group):

    BEGINNER = [('U10', 'NON'), ('U18', 'NON'), ('A18', 'NON'), ('U10', 'PRI'),
                ('U18', 'PRI'), ('A18', 'PRI'), ('U10', 'SEC'), ('U10', 'PTG')]
    INTERMEDIATE = [('U18', 'SEC'), ('A18', 'SEC'),
                    ('U10', 'UDG'), ('U18', 'UDG')]
    ADVANCE = [('U18', 'PTG'), ('A18', 'PTG'), ('U18', 'PTG'), ('A18', 'UDG')]

    pair = (age_group, education_group)
    if pair in BEGINNER:
        return "Beginner", "BEG"
    elif pair in INTERMEDIATE:
        return "Intermediate", "IDT"
    elif pair in ADVANCE:
        return "Advance", "ADV"

    return "Beginner", "BEG"


def index(request):
    if request.user.is_authenticated:
        return render(request, "index.html", {"loggedIn": True})

    else:
        return render(request, "index.html", {"loggedIn": False})


def learn(request):
    date=datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d')
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('index')
        attempts = 0
        try:
            dl = DailyLearner.objects.filter(user=request.user).get()
            if dl.attemptCount>=10 and dl.date == date:
                return render(request, "learn.html", {"loggedIn": True, "limit":True})
            else:
                if dl.attemptCount >= 10:
                    DailyLearner.objects.update(user=request.user, date=date, attemptCount=0)
                    attempts = 0
                else:
                    attempts = dl.attemptCount
        except:
            pass

        level = Learner.objects.filter(user=request.user).get()
        level = level.level
        df_shuffled = database.sample(frac=1, random_state=42)
        if level == 'BGR':
            mask = (df_shuffled['word'].str.len() >=3) & (df_shuffled['word'].str.len()<6) 
            question_row = df_shuffled.loc[mask].sample()
        elif level == 'ITD':
            mask = (df_shuffled['word'].str.len() >=5) & (df_shuffled['word'].str.len()<8) 
            question_row = df_shuffled.loc[mask].sample()
        else:
            mask = (df_shuffled['word'].str.len() >=8) 
            question_row = df_shuffled.loc[mask].sample()
        
        date=datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d')
        return render(request, "learn.html", {"loggedIn": True, "attempts":attempts, "question": question_row['word'].to_string().split()[1],"pos":question_row['pos'].to_string().split()[1], "date": date, "limit":False})

    else:
        return render(request, "learn.html", {"loggedIn": False, "limit":False})


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


def updateLeaderboardDataForUser(user, date, group):
    print(user, date, group)
    try:
        track = TrackDailyChallenge.objects.filter(user=user, date__range=[
                                                   datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'), date]).order_by('-accuracy')
        if track is None:
            return False

        avg, iter = 0, 0
        for tr in track:
            iter += 1
            avg += tr.accuracy
        avg = avg/iter

        try:
            if group == 'MLY':
                trackLb = TrackLeaderboard.objects.update(
                    user=user, group=group, monthly=avg)
            elif group == 'WLY':
                trackLb = TrackLeaderboard.objects.update(
                    user=user, group=group, weekly=avg)
        except:
            if group == 'MLY':
                trackLb = TrackLeaderboard.objects.create(
                    user=user, group=group, monthly=avg)
                trackLb.save()
            elif group == 'WLY':
                trackLb = TrackLeaderboard.objects.create(
                    user=user, group=group, weekly=avg)
                trackLb.save()

        return True
    except:
        return False



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
            personalDetails = UserPersonalDetails.objects.create(
                user=user)
            personalDetails.save()
            trackLbM = TrackLeaderboard.objects.create(
                user=user, group='MLY', monthly=0.00, weekly=0.00)
            trackLbM.save()
            trackLbW = TrackLeaderboard.objects.create(
                user=user, group='WLY', weekly=0.00, monthly=0.00)
            trackLbW.save()
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
    current = Learner.objects.filter(user=request.user)[0]
    return render(request, "editSettings.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "level": current.level})


@login_required
def changePassword(request):
    if request.method == 'POST':
        username = request.POST['username']
        pwd = request.POST['password']
        cpwd = request.POST['confirmPassword']
        if pwd!=cpwd:
            return render(request, "changePassword.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "message":"Passwords does not match!"})
        else:
            if request.user == User.objects.get(username=username):
                u = User.objects.get(username=username)
                u.set_password(pwd)
                u.save()
                return redirect('login')
            else:
                return render(request, "changePassword.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "message":"Invalid username!"})
    else:
        return render(request, "changePassword.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True})


@login_required
def deleteAccount(request):
    if request.method == 'POST':
        username = request.POST['username']
        u = User.objects.get(username=username)
        u.delete()
        return redirect('login')
    else:
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
                date=datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'))
            dc = daily.values()
            if selected == dc[0]['meaning']:
                context['submit'] = True
                context['success'] = True
                context['message'] = "Your answer is right! Come back tomorrow for next challenge!"
                track = TrackDailyChallenge.objects.create(
                    user=request.user, challenge=daily[0], solvedCorrectly=True, accuracy=100.00)
                track.save()
                return render(request, "dailyChallenge.html", context)
            else:
                context['submit'] = True
                context['success'] = False
                context['message'] = "You answer is wrong! The right meaning of the word is " + \
                    dc[0]['meaning']+". See you tomorrow!"
                track = TrackDailyChallenge.objects.create(
                    user=request.user, challenge=daily[0], accuracy=0.00)
                track.save()
                return render(request, "dailyChallenge.html", context)
        except:
            context['message'] = "Could not submit the answer!"
            return render(request, "dailyChallenge.html", context)
    else:
        try:
            track = TrackDailyChallenge.objects.filter(
                user=request.user, date=datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d')).values()
            if track:
                return render(request, "dailyChallenge.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "message": "You have already solved today's challenge, come back tomorrow for new one!"})
            else:
                try:
                    dc = DailyChallenge.objects.filter(
                        date=datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d')).values()
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
            date=datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'))
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
        level, code = determineLevel(age_group=age_group,
                                     education_group=education_group)
        try:
            personalDetails = UserPersonalDetails.objects.filter(
                user=request.user).update(age_group=age_group, education_group=education_group)
        except:
            personalDetails = UserPersonalDetails.objects.create(
                age_group=age_group, education_group=education_group, user=request.user)
            personalDetails.save()
            return render(request, "ageAndEducation.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "message": "Created new preference!", "suggestedLevel": level, "suggestedLevelCode": code})

        return render(request, "ageAndEducation.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "message": "Updated previous preference!", "suggestedLevel": level, "suggestedLevelCode": code})
    else:
        try:
            personalDetails = UserPersonalDetails.objects.filter(
                user=request.user).values()
        except:
            return HttpResponseNotFound('<h1>Error in user profile!</h1>')

        return render(request, "ageAndEducation.html", {"name": request.user.first_name+' '+request.user.last_name, "loggedIn": True, "details": personalDetails[0]})


def updateLeaderboardDataForUser(user, date, group):
    try:
        track = TrackDailyChallenge.objects.filter(user=user, date__range=[
                                                   date, datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d')]).order_by('-accuracy')
        if track is None:
            return False

        avg, iter = 0, 0
        for tr in track:
            iter += 1
            avg += tr.accuracy
        avg = avg/iter
        try:
            if group == 'MLY':
                trackLb = TrackLeaderboard.objects.filter(
                    user=user, group=group).update(monthly=avg)
            elif group == 'WLY':
                trackLb = TrackLeaderboard.objects.filter(
                    user=user, group=group).update(weekly=avg)
        except:
            try:
                if group == 'MLY':
                    trackLb = TrackLeaderboard.objects.create(
                        user=user, group=group, monthly=avg)
                elif group == 'WLY':
                    trackLb = TrackLeaderboard.objects.create(
                        user=user, group=group, weekly=avg)
                trackLb.save()
            except:
                return False

        return True
    except:
        return False


@login_required
def leaderboards(request):
    if request.method == "POST":
        filter = request.POST['filter']
        if filter == 'DLY':
            try:
                track = TrackDailyChallenge.objects.filter(
                    date=datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d')).order_by('-accuracy')
                context = {
                    "name": request.user.first_name+' '+request.user.last_name,
                    "loggedIn": True,
                    "track": track
                }
                return render(request, "leaderboards.html", context)
            except:
                context = {
                    "name": request.user.first_name+' '+request.user.last_name,
                    "loggedIn": True,
                    "message": "Could not load your request!"
                }
                return render(request, "leaderboards.html", context)
        elif filter == 'WLY':
            date = (datetime.now(timezone("Asia/Kolkata")) -
                    dtm.timedelta(days=7)).date()
            print(date)
        elif filter == 'MLY':
            date = (datetime.now(timezone("Asia/Kolkata")) -
                    dtm.timedelta(days=30)).date()
        else:
            return HttpResponseNotFound('<h1>Invalid Filter!</h1>')
        if updateLeaderboardDataForUser(user=request.user, date=date, group=filter):
            try:
                if filter == 'WLY':
                    trackLb = TrackLeaderboard.objects.filter(
                        group=filter).order_by('-weekly')
                elif filter == 'MLY':
                    trackLb = TrackLeaderboard.objects.filter(
                        group=filter).order_by('-monthly')
            except:
                context = {
                    "name": request.user.first_name+' '+request.user.last_name,
                    "loggedIn": True,
                    "message": "Could not load your request!"
                }
                return render(request, "leaderboards.html", context)
            context = {
                "name": request.user.first_name+' '+request.user.last_name,
                "loggedIn": True,
                "data": trackLb.values()
            }
            return render(request, "leaderboards.html", context)
        else:
            context = {
                "name": request.user.first_name+' '+request.user.last_name,
                "loggedIn": True,
                "message": "Could not load your request!"
            }
            return render(request, "leaderboards.html", context)
    else:
        try:
            track = TrackDailyChallenge.objects.filter(
                date=datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d')).order_by('-accuracy')
            context = {
                "name": request.user.first_name+' '+request.user.last_name,
                "loggedIn": True,
                "track": track
            }
            return render(request, "leaderboards.html", context)
        except:
            context = {
                "name": request.user.first_name+' '+request.user.last_name,
                "loggedIn": True,
                "message": "Could not load your request!"
            }
            return render(request, "leaderboards.html", context)

@login_required
def learn_form_check(request):

    if request.method == "POST":
        word = request.POST['word']
        sentence = request.POST['answer']
        source = database[database['word']==word]
        source_sentences = []
        for rows in source['def']:
            source_sentences.append(rows)

        output = query({
            "inputs": {
                "source_sentence": sentence,
                "sentences": source_sentences
            },
        })

        max_output = np.argmax(output)
        meaning = source_sentences[max_output]
        date=datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d')

        try:
            du = DailyLearner.objects.filter(user=request.user).get()
            if str(date) == str(du.date):
                DailyLearner.objects.filter(user=request.user).update(attemptCount = du.attemptCount+1, latest_ans=meaning)
            else:
                DailyLearner.objects.filter(user=request.user).update(attemptCount = 0, date = date, latest_ans=meaning)
        except:
            du = DailyLearner.objects.create(user=request.user, attemptCount=1, latest_ans=meaning)
            du.save()

        return render(request, "learn_submit.html", {"loggedIn": True, "score": output[max_output]*100, "meaning": meaning})
    else:
        return HttpResponseNotFound('<h1>Bad request!</h1>')

    