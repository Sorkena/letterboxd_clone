from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from rest_framework import viewsets
from movies.models import Review, Movie
from users.forms import CustomListForm
from users.models import CustomList


class UsersViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        all_users = User.objects.all()
        return render(request, 'users/users.html', {'all_users': all_users})


class UserProfileViewSet(viewsets.ViewSet):
    def profile(self, request, username, *args, **kwargs):
        profile_user = get_object_or_404(User, username=username)
        user_reviews = Review.objects.filter(user=profile_user).order_by('-reviewed_at')

        watchlist_movies = []
        if hasattr(profile_user, 'watchlist'):
            watchlist_movies = profile_user.watchlist.movies.all()

        custom_lists = profile_user.custom_lists.all().order_by('-created_at')

        return render(request, 'users/profile.html', {
            'profile_user': profile_user,
            'user_reviews': user_reviews,
            'watchlist_movies': watchlist_movies,
            'custom_lists': custom_lists
        })


class CustomListViewSet(viewsets.ViewSet):

    def create_list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')

        if request.method == 'GET':
            form = CustomListForm()

        else:
            form = CustomListForm(request.data)

            if form.is_valid():
                custom_list = form.save(commit=False)
                custom_list.user = request.user
                custom_list.save()
                return redirect('user_profile', username=request.user.username)

        return render(request, 'users/custom_list_form.html', {'form': form})


    def retrieve(self, request, username, list_id, *args, **kwargs):
        list_owner = get_object_or_404(User, username=username)
        custom_list = get_object_or_404(CustomList, id=list_id, user=list_owner)

        if request.method == 'POST':
            if not request.user.is_authenticated or request.user.username != username:
                return redirect('home')

            if 'remove_movie' in request.data:
                movie_id = request.data.get('movie_id')
                movie = get_object_or_404(Movie, id=movie_id)
                custom_list.movies.remove(movie)

            return redirect('custom_list_detail', username=username, list_id=list_id)

        movies = custom_list.movies.all()

        return render(request, 'users/custom_list_detail.html', {
            'custom_list': custom_list,
            'movies': movies,
            'list_owner': list_owner
        })


    def edit(self, request, username, list_id, *args, **kwargs):
        if not request.user.is_authenticated or request.user.username != username:
            return redirect('home')

        custom_list = get_object_or_404(CustomList, id=list_id, user=request.user)

        if request.method == 'POST':

            if 'delete_list' in request.data:
                custom_list.delete()
                return redirect('user_profile', username=request.user.username)

            form = CustomListForm(request.data, instance=custom_list)

            if form.is_valid():
                form.save()
                return redirect('custom_list_detail', username=username, list_id=list_id)

        else:
            form = CustomListForm(instance=custom_list)

        return render(request, 'users/custom_list_form.html', {
            'form': form,
            'custom_list': custom_list
        })