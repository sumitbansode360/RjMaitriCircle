from django.urls import path, include
from userauths.views import RegisterView, Loginview, LogOutView, EditProfileView, Follower_List, Following_List, Search, activate_account

urlpatterns = [
    path('search/', Search, name="search"), #search
    path('register/', RegisterView, name="register"),
    path('activate/<uidb64>/<token>/', activate_account, name='activate'),
    path('sign-in/', Loginview, name="sign-in"),
    path('sign-out/',LogOutView, name="sign-out"),
    path('edit-profile/', EditProfileView, name="EditProfileView"),
    path('<username>/followers/', Follower_List, name="Follower_List"),
    path('<username>/following/', Following_List, name="Following_List"),
]
