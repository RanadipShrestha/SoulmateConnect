from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Home)

class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'dob', 'profile' , 'city' ,'occupation', 'education', 'hobbies', 'gender')
    search_feilds = ('user_username', 'phone_numebr')


admin.site.register(Like)
admin.site.register(Match)
admin.site.register(Notification)
admin.site.register(FriendRequest)