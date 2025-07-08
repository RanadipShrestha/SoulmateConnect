from django.contrib import admin
from .models import userDetails
# Register your models here.

class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'dob', 'profile' , 'city' ,'occupation', 'education', 'hobbies', 'gender')
    search_feilds = ('user_username', 'phone_numebr')

admin.site.register(userDetails, UserDetailsAdmin),
