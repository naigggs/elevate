from django.urls import path
from .views import *

urlpatterns = [
    path('', landingpage, name='landingpage'),
    path('signup/', signup, name='signup'),
    path('signin/', signin, name='signin'),
    path('logout/', logout, name='logout'),
    # path('index/', index, name="index"),
    path('add_user_info/', add_user_info, name='add_user_info'),
    path('profile/<str:username>/', profile, name='profile'),
    path('unfriend/<str:username>/', unfriend, name='unfriend'),
    path('send_friend_request/<int:to_user_id>/', send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:request_id>/', accept_friend_request, name='accept_friend_request'),
    path('decline_friend_request/<int:request_id>/', decline_friend_request, name='decline_friend_request'),
    path('friend_requests/', friend_requests, name='friend_requests'),
    path('change_password/', change_password, name='change_password'),
    path('change_user_info/', change_user_info, name='change_user_info'),
    path('search/', user_search, name='user_search'),
    # path('profile/<int:profile_id>/comment/', add_comment, name='add_comment'),
    # ADMIN URLS
    path('mod/user-list/', user_list, name='user_list'),
    path('mod/edit/<int:user_id>/', edit_user, name='edit_user'),
    path('mod/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('mod/addprofanity', add_profanity_word, name='add_profanity_word'),
    path('mod/delete-profanity/<int:word_id>/', delete_profanity_word, name='delete_profanity_word'),
]