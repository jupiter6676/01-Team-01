from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

# User = get_user_model()

# # Register your models here.
# class MyUserAdmin(UserAdmin):
#     model = User
#     list_display = ['username', 'nickname', 'username', 'email']
    
#     # 유저 정보 관리 페이지 정보 입력창 추가
#     fieldsets = UserAdmin.fieldsets + (
#         (None, {'fields': ('nickname', 'img_profile',)}),
#     )


# admin.site.register(User, MyUserAdmin)