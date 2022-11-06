from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
from django.http import JsonResponse
from django.core.paginator import Paginator

# Create your views here.
def index(request):
    articles = Articles.objects.order_by("-pk")
    page = request.GET.get("page", "1")
    paginator = Paginator(articles, 10)
    page_obj = paginator.get_page(page)
    context = {
        "articles": page_obj,
    }
    return render(request, "community/index.html", context)


def detail(request, pk):
    article = get_object_or_404(Articles, pk=pk)
    default_view_count = article.view_count
    article.view_count = default_view_count + 1
    article.save()
    comment_form = CommentsForm()
    comments = article.comments_set.filter(parent_comment=None)
    replies= article.comments_set.exclude(parent_comment=None)

    context = {
        "article": article,
        "comments": comments,
        "replies": replies,
        "comment_form": comment_form,
        "photo_cnt": article.photo_set.count(),
    }

    return render(request, "community/detail.html", context)


@login_required
def create(request):
    if request.method == "POST":
        article_form = ArticlesForm(request.POST, request.FILES)
        photo_form = PhotoForm(request.POST, request.FILES)
        images = request.FILES.getlist("image")

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
            return redirect("community:index")
    else:
        article_form = ArticlesForm()
        photo_form = PhotoForm()
    context = {
        "article_form": article_form,
        "photo_form": photo_form,
    }
    return render(request, "community/create.html", context)



@login_required
def update(request, pk):
    article = Articles.objects.get(pk=pk)
    photos = Photo.objects.filter(article_id=article.pk)
    if request.user != article.user:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()
    if request.method == "POST":
        article_form = ArticlesForm(request.POST, request.FILES, instance=article)
        photo_form = PhotoForm(request.POST, request.FILES)
        images = request.FILES.getlist("image")

        for photo in photos:
            if photo.image:
                photo.delete()
        if article_form.is_valid() and photo_form.is_valid():
            article = article_form.save(commit=False)         
            if len(images):
                for image in images:
                    image_instance = Photo(article=article, image=image)
                    article.save()
                    image_instance.save()
            else:
                article.save()
            return redirect("community:detail", pk)
    else:
        article_form = ArticlesForm(instance=article)
        if photos:
            photo_form = PhotoForm(instance=photos[0])
        else:
            photo_form = PhotoForm()

    context = {
        "article_form": article_form,
        "photo_form": photo_form,
    }
    return render(request, "community/create.html", context)


@login_required
def delete(request, pk):
    article = Articles.objects.get(pk=pk)

    if request.user != article.user:
        return redirect("community:index")

    if request.method == "POST":
        if request.user == article.user:
            article.delete()
            return redirect("community:index")
    else:
        return redirect("community:detail", pk)


@login_required
def like(request, pk):
    article = Articles.objects.get(pk=pk)
    if article.like_users.filter(id=request.user.id).exists():
        article.like_users.remove(request.user)
        is_liked = False
    else:
        article.like_users.add(request.user)
        is_liked = True
    context = {
        'isLiked': is_liked,
        'likeCount': article.like_users.count()
    }
    return JsonResponse(context)


@login_required
def comment_create(request, pk):
    if request.user.is_authenticated:
        article = get_object_or_404(Articles, pk=pk)
        comment_form = CommentsForm(request.POST)
        parent_comment_id = request.POST.get('parent_comment_id', None)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.article = article
            comment.user = request.user
            comment.parent_comment_id = parent_comment_id
            comment.save()
            return redirect('community:detail', article.pk)
    return redirect('community:login')


@login_required
def comment_delete(request, article_pk, comment_pk):
    if request.user.is_authenticated:
        article = Articles.objects.get(pk=article_pk)
        comment = Comments.objects.get(pk=comment_pk)
        replies = article.comments_set.filter(parent_comment=comment)

        if request.user == comment.user:
            comment.delete()
    return redirect('community:detail', article_pk)


@login_required
def comment_update(request, article_pk, comment_pk):
    comment = Comments.objects.get(pk=comment_pk)
    comment_form = CommentsForm(instance=comment)
    if request.user != comment.user:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()
    if request.method == "POST":
        form = CommentsForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('community:detail', article_pk)
    else:
        form = CommentsForm(instance=comment)
    return render('community:comment_update', {"form": form})


@login_required
def comment_like(request, article_pk, comment_pk):
    comment = get_object_or_404(Comments, pk=comment_pk)
    article = Articles.objects.get(pk=article_pk)
    if request.user in comment.like_users.all():
        comment.like_users.remove(request.user)
    else:
        comment.like_users.add(request.user)
    return redirect("community:detail", article_pk)


