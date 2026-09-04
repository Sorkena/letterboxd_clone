from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User

from movies.models import Review


def users(request):
  all_users = User.objects.all()
  return render(request, 'users/users.html', {'all_users': all_users})


def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    user_reviews = Review.objects.filter(user=profile_user).order_by('-reviewed_at')

    return render(request, 'users/profile.html', {
        'profile_user': profile_user,
        'user_reviews': user_reviews
    })