from django.urls import path
from .views import *

urlpatterns = [

    path('registration/',
         UserRegister.as_view(),
         name='registration'),

    path('registration/submit/',
         UserRegisterFormHandle.as_view(),
         name='registration_submit'),

    path('login/',
         auth_views.LoginView.as_view(),
         name='login'),

    path('logout/',
         auth_views.LogoutView.as_view(),
         name='logout'),

    path('password_change/',
         auth_views.PasswordChangeView.as_view(),
         name='password_change'),

    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),

    path('profile/<str:username>/',
         Profile.as_view(),
         name='profile'),

    path('profile/<str:username>/friends/',
         FriendList.as_view(),
         name='friends_list'),

    path('profile/<str:username>/add_friend/',
         FriendRequestFormHandle.as_view(),
         name='add_friend'),

    path('profile/<str:username>/accept_request/',
         AcceptFriendRequest.as_view(),
         name='accept_request'),

    path('profile/<str:username>/decline_request/',
         DeclineFriendRequest.as_view(),
         name='decline_request'),

    path('profile/<str:username>/friend_requests/',
         FriendRequestList.as_view(),
         name='friend_requests_list'),

    path('profile/<str:username>/remove_friend/',
         RemoveFriend.as_view(),
         name='remove_friend'),

    path('profile/<str:username>/edit/',
         EditProfile.as_view(),
         name='edit_profile'),

    path('password_reset/',
         auth_views.PasswordResetView.as_view(),
         name='password_reset'),

    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),

    path('reset/done',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),

    path('user_list/',
         UserList.as_view(),
         name='user_list'),
]
