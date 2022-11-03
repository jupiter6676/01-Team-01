from xml.etree.ElementTree import Comment
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import *
from .forms import *
import locale
import json


# Create your views here.
def index(request):

    articles = Article.objects.order_by("-pk")

    context = {
        "articles": articles,
    }
    return render(request, "articles/index.html", context)


def create(request):
    if request.method == "POST":
        article_form = ArticleForm(request.POST, request.FILES)
        photo_form = PhotoForm(request.POST, request.FILES)
        images = request.FILES.getlist("image")
        tags = request.POST.get("tags", "").split(",")

        if article_form.is_valid() and photo_form.is_valid():
            article = article_form.save(commit=False)
            article.user = request.user

            if len(images):
                for image in images:
                    image_instance = Photo(article=article, image=image)
                    article.save()
                    image_instance.save()

            else:
                article.save()
                for tag in tags:
                    tag = tag.strip()
                    article.tags.add(tag)
                    article.save()

            return redirect("articles:index")
    else:
        article_form = ArticleForm()
        photo_form = PhotoForm()
    context = {
        "article_form": article_form,
        "photo_form": photo_form,
    }
    return render(request, "articles/create.html", context)


def detail(request, pk):
    article = Article.objects.get(pk=pk)
    comment_form = CommentForm()

    context = {
        "article": article,
        "comments": article.comment_set.all(),
        "comment_form": comment_form,
        "photo_cnt": article.photo_set.count(),
    }
    return render(request, "articles/detail.html", context)


@login_required
def delete(request, pk):
    article = Article.objects.get(pk=pk)
    if request.user != article.user:
        return redirect("articles:index")
    if request.method == "POST":
        if request.user == article.user:
            article.delete()
            return redirect("articles:index")
    else:
        return redirect("articles:detail", pk)


@login_required
def update(request, pk):
    article = Article.objects.get(pk=pk)
    photos = Photo.objects.filter(article_id=article.pk)
    tags_ = article.tags.all()  # 기존에 있었던 태그(삭제)
    
    if tags_:
        for tag in tags_:
            tag.delete()

    if request.method == "POST":
        # POST : input 값 가져와서, 검증하고, DB에 저장
        article_form = ArticleForm(request.POST, request.FILES, instance=article)
        photo_form = PhotoForm(request.POST, request.FILES)
        images = request.FILES.getlist("image")
        tags = request.POST.get("tags", "").split(",")

        # Article.objects.filter(record_Id=1).update(city=None) #잔여물
        

        for photo in photos:
            if photo.image:
                photo.delete()
        if article_form.is_valid() and photo_form.is_valid():
            article = article_form.save(commit=False)

            # 유효성 검사 통과하면 저장하고, 상세보기 페이지로
            if len(images):
                for image in images:
                    image_instance = Photo(article=article, image=image)
                    article.save()
                    image_instance.save()
            else:
                article.save()
                for tag in tags:
                    tag = tag.strip()
                    article.tags.add(tag)
                    article.save()

            return redirect("articles:index")

    else:
        article_form = ArticleForm(instance=article)
        if photos:
            photo_form = PhotoForm(instance=photos[0])
        else:
            photo_form = PhotoForm()

    context = {
        "article_form": article_form,
        "photo_form": photo_form,
    }
    return render(request, "articles/create.html", context)


def like(request, pk):
    article = Article.objects.get(pk=pk)
    if request.user in article.like_users.all():
        article.like_users.remove(request.user)
    else:
        article.like_users.add(request.user)
    return redirect("articles:detail", pk)


def bookmark(request, pk):
    article = Article.objects.get(pk=pk)
    if request.user in article.bookmark_users.all():
        article.bookmark_users.remove(request.user)
    else:
        article.bookmark_users.add(request.user)
    return redirect("articles:detail", pk)


@login_required
def comment_create(request, pk):
    article = Article.objects.get(pk=pk)
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.article = article
        comment.user = request.user
        comment.save()
    return redirect("articles:detail", article.pk)


@login_required
def comment_delete(request, article_pk, comment_pk):
    if request.user.is_authenticated:
        comment = Comment.objects.get(pk=comment_pk)
        if request.user == comment.user:
            comment.delete()
    return redirect("articles:detail", article_pk)


@login_required
def comment_update(request, article_pk, comment_pk):
    comment = Comment.objects.get(pk=comment_pk)
    comment_form = CommentForm(instance=comment)
    if request.user != comment.user:
        from django.http import HttpResponseForbidden

        return HttpResponseForbidden()
    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect("articles:detail", article_pk)
    else:
        form = CommentForm(instance=comment)
    return render("articles:comment_update", {"form": form})


# @login_required
# def comment_like(request, article_pk, comment_pk):
#     comment = get_object_or_404(Comment, pk=comment_pk)
#     if comment.like_users.filter(pk=request.user.pk).exists():
#   # if request.user in comment.like_users.all():
#         comment.like_users.remove(request.user)
#         is_comment_liked = False
#     else:
#         comment.like_users.add(request.user)
#         is_comment_liked = True
#     context = {
#         "is_comment_liked": is_comment_liked,
#         "comment_like_count": comment.like_users.count(),
#     }
#     return JsonResponse(context)


@login_required
def comment_like(request, article_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    article = Article.objects.get(pk=article_pk)
    if request.user in comment.like_users.all():
        comment.like_users.remove(request.user)
    else:
        comment.like_users.add(request.user)
    return redirect("articles:detail", article_pk)
