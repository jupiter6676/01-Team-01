from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import *
from .forms import *
from django.db.models import Q


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
        
        # if request.POST.get("tags", "") != "":
        #     tags = request.POST.get("tags", "").split(",")
        # else:
        #     tags = None

        if article_form.is_valid() and photo_form.is_valid():
            article = article_form.save(commit=False)
            article.user = request.user

            if len(images):
                for image in images:
                    image_instance = Photo(article=article, image=image)
                    article.save()
                    image_instance.save()

            article.save()
            if tags:
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
    default_view_count = article.view_count
    article.view_count = default_view_count + 1
    article.save()
    comment_form = CommentForm()
    comments = article.comment_set.filter(parent_comment=None)
    replies = article.comment_set.exclude(parent_comment=None)

    context = {
        "article": article,
        "comments": comments,
        "replies": replies,
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

    if article.like_users.filter(pk=request.user.pk).exists():
        article.like_users.remove(request.user)
        is_liked = False
    else:
        article.like_users.add(request.user)
        is_liked = True

    data = {
        "isLiked": is_liked,
        "likeCount": article.like_users.count(),
    }

    return JsonResponse(data)


def bookmark(request, pk):
    article = Article.objects.get(pk=pk)
    
    if request.user in article.bookmark_users.all():
        article.bookmark_users.remove(request.user)
        is_bookmarked = False
    else:
        article.bookmark_users.add(request.user)
        is_bookmarked = True

    data = {
        "isBookmarked": is_bookmarked,
    }

    return JsonResponse(data)


@login_required
def comment_create(request, pk):
    article = Article.objects.get(pk=pk)
    comment_form = CommentForm(request.POST)
    parent_comment_id = request.POST.get("parent_comment_id", None)

    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.article = article
        comment.user = request.user
        comment.parent_comment_id = parent_comment_id
        comment.save()

    data = {
        'parent_comment_pk': parent_comment_id,
        'comment_pk': comment.pk,
        'user_pk': comment.user.pk,
        'nickname': comment.user.nickname,
        'content': comment.content,
        'created_at': comment.created_at,
        'commentLikeCount': comment.like_users.count(),
        'commentCount': article.comment_set.count(),
    }

    # return redirect("articles:detail", article.pk)
    return JsonResponse(data)


@login_required
def comment_delete(request, article_pk, comment_pk):
    article = Article.objects.get(pk=article_pk)
    comment = Comment.objects.get(pk=comment_pk)
    replies = article.comment_set.filter(parent_comment=comment)
    
    print(replies)

    if request.user.is_authenticated:
        comment = Comment.objects.get(pk=comment_pk)
        is_deleted = False

        if request.user == comment.user:
            is_deleted = True

            if replies:
                is_parent = True
                parent_comment_pk = comment.pk
            else:
                is_parent = False
                parent_comment_pk = None

            comment.delete()

    data = {
        'parent_comment_pk': parent_comment_pk,
        'is_deleted': is_deleted,
        'is_parent': is_parent,
        'commentCount': article.comment_set.count(),
    }

    return JsonResponse(data)


# @login_required
# def comment_update(request, comment_pk, article_pk):
#     comment = Comment.objects.get(pk=comment_pk)
#     com_form = CommentForm(instance=comment)
#     if request.user != comment.user:
#         from django.http import HttpResponseForbidden

#         return HttpResponseForbidden()
#     if request.method == "POST":
#         comment_form = CommentForm(request.POST, instance=comment)
#         if comment_form.is_valid():
#             comment_form.save()
#             return redirect("articles:detail", article_pk)
#     # else:
#     #     form = CommentForm(instance=comment)
#     context = {
#         "com_form": com_form,
#     }
#     return render(request, "articles/comment_update.html", context)


@login_required
def comment_like(request, article_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    article = Article.objects.get(pk=article_pk)

    if request.user in comment.like_users.all():
        comment.like_users.remove(request.user)
        is_liked = False
    else:
        comment.like_users.add(request.user)
        is_liked = True

    data = {
        "isLiked": is_liked,
        "likeCount": comment.like_users.count(),
    }

    return JsonResponse(data)


# 검색
def search(request):
    search_keyword = request.GET.get("search", "")
    search_option = request.GET.get(
        "search_option", ""
    )  # title, title_content, hashtag, user
    articles = Article.objects.order_by("-pk")

    if search_keyword:
        if search_option == "title":
            search_articles = articles.filter(title__icontains=search_keyword)
        elif search_option == "title_content":
            # Q: ORM WHERE에서 or 연산을 수행
            search_articles = articles.filter(
                Q(title__icontains=search_keyword)
                | Q(content__icontains=search_keyword)
            )
        elif search_option == "hashtag":
            # distinct(): 중복 제거
            # 만약 해시태그가 #1, #11, #111인 글이 하나 있고, 1을 검색하면
            # 같은 글이 3개가 보여짐.
            search_articles = articles.filter(
                tags__name__icontains=search_keyword
            ).distinct()
        elif search_option == "user":
            # ForeignKey icontains
            # {Article의 User field}__{User의 nickname field}__icontains
            search_articles = articles.filter(
                Q(user__nickname__icontains=search_keyword)
            )

    context = {
        "search_articles": search_articles,
    }

    return render(request, "articles/search.html", context)


def roulette(request):
    return render(request, "articles/roulette.html")