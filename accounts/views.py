from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile
from .forms import CustomUserCreationForm, ProfileForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .forms import CustomUserChangeForm
from django.http import JsonResponse


# Create your views here.
def signup(request):
    if request.user.is_authenticated:
        return redirect("articles:index")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)  # 프로필 생성
            auth_login(request, user)
            return redirect("articles:index")
    else:
        form = CustomUserCreationForm()
    context = {"form": form}
    return render(request, "accounts/signup.html", context)


def login(request):
    if request.user.is_authenticated:
        return redirect("articles:index")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect(request.GET.get("next") or "articles:index")
    else:
        form = AuthenticationForm()
    context = {"form": form}
    return render(request, "accounts/login.html", context)


def logout(request):
    auth_logout(request)
    messages.warning(request, "로그아웃 되었습니다.")
    return redirect("articles:index")


def detail(request, pk):
    user = get_user_model().objects.get(pk=pk)
    articles = user.article_set.all()
    like_articles = user.like_articles.all()
    bookmark_articles = user.bookmark_articles.all()

    context = {
        "user": user, 
        "articles": articles, 
        "like_articles": like_articles,
        "bookmark_articles": bookmark_articles,
    }
    return render(request, "accounts/detail.html", context)


@require_POST
@login_required
def follow(request, pk):
    user = get_object_or_404(get_user_model(), pk=pk)

    # 프로필에 해당하는 유저를 로그인한 유저가 팔로우 할 수 없음
    if request.user == user:
        messages.warning(request, "스스로 팔로우 할 수 없습니다.")
        return redirect("accounts:detail", pk)

    # 팔로우 상태면, 팔로우 취소를 누르면 삭제
    if request.user in user.followers.all():
        user.followers.remove(request.user)
        is_followed = False

    # 팔로우 상태가 아니면, '팔로우'를 누르면 추가
    else:
        user.followers.add(request.user)
        is_followed = True

    data = {
        "followers_count": user.followers.count(),
        "followings_count": user.followings.count(),
        "is_followed": is_followed,
    }

    return JsonResponse(data)


# 마이 페이지 (회원 정보로 이동, 비밀번호 변경, 로그아웃, 회원탈퇴)
@login_required
def mypage(request, user_pk):
    user = get_object_or_404(get_user_model(), pk=user_pk)

    if request.user != user:
        return redirect("articles:index")

    context = {
        "user": user,
    }

    return render(request, "accounts/mypage.html", context)


# 비밀번호 변경
@login_required
def password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # 로그인 유지
            return redirect("accounts:mypage", request.user.pk)

    else:
        form = PasswordChangeForm(request.user)

    context = {
        "form": form,
    }

    return render(request, "accounts/password.html", context)


# 회원 탈퇴
def delete(request):
    if request.user.is_authenticated:
        request.user.delete()
        auth_logout(request)

    return redirect("articles:index")


# 회원 프로필 (프로필 사진, 소개글) (+ 닉네임?)
@login_required
def update(request, pk):
    user = get_object_or_404(get_user_model(), pk=pk)

    # 업데이트
    if request.user.profile:
        profile = request.user.profile

        if request.method == "POST":
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
            change_form = CustomUserChangeForm(request.POST, instance=user)

            if profile_form.is_valid() and change_form.is_valid():
                profile_form.save()
                change_form.save()
                # return redirect('accounts:detail', request.user.pk)
                return redirect("accounts:mypage", request.user.pk)

        else:
            profile_form = ProfileForm(instance=profile)
            change_form = CustomUserChangeForm(instance=user)

    # 최초 생성
    else:
        if request.method == "POST":
            profile_form = ProfileForm(request.POST, request.FILES)
            change_form = CustomUserChangeForm(request.POST, instance=user)

            if profile_form.is_valid() and change_form.is_valid():
                profile_form.save()
                change_form.save()
                # return redirect('accounts:detail', request.user.pk)
                return redirect("accounts:mypage", request.user.pk)

        else:
            profile_form = ProfileForm()
            change_form = CustomUserChangeForm(instance=user)

    context = {
        "profile_form": profile_form,
        "change_form": change_form,
    }

    return render(request, "accounts/update.html", context)


@login_required
def articles(request, pk):
    articles = all.Articles.objects.filter(user=request.user).order_by("-pk")
    context = {
        "articles": articles,
    }
    return render(request, "accounts/articles.html", context)
