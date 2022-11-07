# URL설정을 app 단위로!
from django.urls import path
from . import views

app_name = "articles"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("<int:pk>/", views.detail, name="detail"),
    path("<int:pk>/delete/", views.delete, name="delete"),
    path("<int:pk>/update/", views.update, name="update"),
    path("<int:pk>/like/", views.like, name="like"),
    path("<int:pk>/bookmark/", views.bookmark, name="bookmark"),
    path("<int:pk>/comments/", views.comment_create, name="comment_create"),
    path(
        "<int:article_pk>/comments/<int:comment_pk>/delete/",
        views.comment_delete,
        name="comment_delete",
    ),
    path(
        "<int:article_pk>/comments/<int:comment_pk>/like/",
        views.comment_like,
        name="comment_like",
    ),
    path("search/", views.search, name="search"),
    path("roulette/", views.roulette, name="roulette"),
]
