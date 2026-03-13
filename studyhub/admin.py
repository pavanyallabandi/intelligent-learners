from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudyGroup, GroupMembership, Video, UserProgress

admin.site.register(User, UserAdmin)
admin.site.register(StudyGroup)
admin.site.register(GroupMembership)
admin.site.register(Video)
admin.site.register(UserProgress)
