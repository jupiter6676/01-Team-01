from xml.etree.ElementTree import Comment
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *


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
def update(request, pk):
    article = Article.objects.get(pk=pk)
    if request.user == article.user:
        if request.method == "POST":
            # POST : input 값 가져와서, 검증하고, DB에 저장
            article_form = ArticleForm(request.POST, request.FILES, instance=article)
            if article_form.is_valid():
                # 유효성 검사 통과하면 저장하고, 상세보기 페이지로
                article_form.save()
                messages.success(request, "글이 수정되었습니다.")
                return redirect("articles:detail", article.pk)
            # 유효성 검사 통과하지 않으면 => context 부터해서 오류메시지 담긴 article_form을 랜더링
        else:
            # GET : Form을 제공
            article_form = ArticleForm(instance=article)
        context = {"article_form": article_form}
        return render(request, "articles/form.html", context)
    else:

        messages.warning(request, "작성자만 수정할 수 있습니다.")
        return redirect("articles:detail", article.pk)


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


# @login_required
# def comment_update(request, article_pk, comment_pk):
#     comment = Comment.objects.get(pk=comment_pk)
#     comment_form = CommentForm(instance=comment)
#     if request.user != comment.user:
#         from django.http import HttpResponseForbidden
#         return HttpResponseForbidden()
#     if request.method == "POST":
#         form = CommentForm(request.POST, instance=comment)
#         if form.is_valid():
#             form.save()
#             return redirect('articles:detail', article_pk)
#     else:
#         form = CommentForm(instance=comment)
#     return render('articles:comment_update', {"form": form})


def like(request, pk):
    article = Article.objects.get(pk=pk)
    if request.user in article.like_users.all():
        article.like_users.remove(request.user)
    else:
        article.like_users.add(request.user)
    return redirect("articles:detail", pk)
