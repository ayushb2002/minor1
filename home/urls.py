from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('learn', views.learn, name="learn"),
    path('login', views.login_view, name="login"),
    path('register', views.register, name="register"),
    path('signup', views.signup, name="signup"),
    path('signin', views.signin, name="signin"),
    path('settings', views.loggedInView, name="settings"),
    path('logout', views.logout_view, name="logout"),
    path('editSettings', views.editSettings, name="editSettings"),
    path('changePassword', views.changePassword, name="changePassword"),
    path('deleteAccount', views.deleteAccount, name="deleteAccount"),
    path('updateLearner', views.updateLearner, name="updateLearner"),
    path('dailyChallenge', views.dailyChallenge, name="dailyChallenge"),
    path('addDailyChallenge', views.addDailyChallenge, name="addDailyChallenge"),
    path('addedDailyChallenge', views.addedDailyChallenge,
         name="addedDailyChallenge"),
    path('trackChallenges', views.track, name="trackChallenges"),
    path('userPersonalDetails', views.userPersonalDetails,
         name="userPersonalDetails"),
     path('leaderboards', views.leaderboards, name="leaderboards"),
     path('learn_form_check', views.learn_form_check, name="learn_form_check"),
     path('sentenceCheck', views.sentenceCheck, name="sentenceCheck"),
     path('getUserById/<int:id>/', views.getUserById, name="getUserById")
]
