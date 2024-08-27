from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(FriendRequest)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(ProfanityWord)