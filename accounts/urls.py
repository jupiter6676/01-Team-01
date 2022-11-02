from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("<int:pk>/", views.detail, name="detail"),
    path("<int:pk>/follow/", views.follow, name="follow"),
    path("<int:user_pk>/mypage/", views.mypage, name="mypage"), # 마이페이지
    path("password/", views.password, name='password'), # 비밀번호 변경
    path("delete/", views.delete, name="delete"),    # 회원탈퇴
    path("<int:pk>/update/", views.update, name="update"),
]
