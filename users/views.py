from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from rest_framework import viewsets
from movies.models import Review, Movie, MovieRating
from users.forms import CustomListForm
from users.models import CustomList, Follow
from django.core.paginator import Paginator
from django.db.models import Count


class UsersViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        all_users = User.objects.all()
        return render(request, 'users/users.html', {'all_users': all_users})


class UserProfileViewSet(viewsets.ViewSet):

    def profile(self, request, username, *args, **kwargs):
        profile_user = get_object_or_404(User, username=username)
        user_reviews = Review.objects.filter(user=profile_user).select_related('movie').order_by('-reviewed_at')[:3]

        review_count = Review.objects.filter(user=profile_user).count()
        watched_count = MovieRating.objects.filter(user=profile_user).count()
        watchlist_count = 0
        if hasattr(profile_user, 'watchlist'):
            watchlist_count = profile_user.watchlist.movies.count()

        custom_lists = profile_user.custom_lists.annotate(movie_count=Count('movies')).order_by('-created_at')[:3]
        custom_list_count = profile_user.custom_lists.count()

        followers_count = profile_user.followers.count()
        following_count = profile_user.following.count()
        is_following = False

        if request.user.is_authenticated and request.user != profile_user:
            is_following = Follow.objects.filter(follower=request.user,following=profile_user).exists()

        return render(request, 'users/profile.html', {
            'profile_user': profile_user,
            'user_reviews': user_reviews,
            'review_count': review_count,
            'watched_count': watched_count,
            'watchlist_count': watchlist_count,
            'custom_lists': custom_lists,
            'followers_count': followers_count,
            'following_count': following_count,
            'is_following': is_following,
            'custom_list_count': custom_list_count,
        })
    def watched(self, request, username, *args, **kwargs):
        profile_user = get_object_or_404(User, username=username)

        watched_ratings = MovieRating.objects.filter(
            user=profile_user
        ).select_related(
            'movie'
        ).order_by('-updated_at')

        paginator = Paginator(watched_ratings, 20)
        page_obj = paginator.get_page(request.query_params.get('page'))

        return render(request, 'users/watched_movies.html', {
            'profile_user': profile_user,
            'page_obj': page_obj
        })

    def watchlist(self, request, username, *args, **kwargs):
        profile_user = get_object_or_404(User, username=username)

        if hasattr(profile_user, 'watchlist'):
            movies = profile_user.watchlist.movies.all().order_by('title')
        else:
            movies = Movie.objects.none()

        paginator = Paginator(movies, 20)
        page_obj = paginator.get_page(request.query_params.get('page'))

        return render(request, 'users/watchlist.html', {
            'profile_user': profile_user,
            'page_obj': page_obj
        })

    def reviews(self, request, username, *args, **kwargs):
        profile_user = get_object_or_404(User, username=username)

        reviews = Review.objects.filter(user=profile_user).select_related('movie').order_by('-reviewed_at')

        paginator = Paginator(reviews, 10)
        page_obj = paginator.get_page(request.query_params.get('page'))

        return render(request, 'users/review_list.html', {
            'profile_user': profile_user,
            'page_obj': page_obj
        })


class CustomListViewSet(viewsets.ViewSet):

    def create_list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')

        form = CustomListForm()

        return render(request, 'users/custom_list_form.html', {'form': form})

    def save_list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')
        form = CustomListForm(request.data)

        if form.is_valid():
            custom_list = form.save(commit=False)
            custom_list.user = request.user
            custom_list.save()
            return redirect('user_profile', username=request.user.username)

        return render(request, 'users/custom_list_form.html', {'form': form})

    def retrieve(self, request, username, list_id, *args, **kwargs):
        list_owner = get_object_or_404(User, username=username)
        custom_list = get_object_or_404(CustomList,id=list_id,user=list_owner)

        movies = custom_list.movies.all().order_by('title')

        paginator = Paginator(movies, 20)
        page_obj = paginator.get_page(request.query_params.get('page'))

        return render(request, 'users/custom_list_detail.html', {
            'custom_list': custom_list,
            'page_obj': page_obj,
            'list_owner': list_owner
        })

    def remove_movie(self, request, username, list_id, *args, **kwargs):
        if not request.user.is_authenticated or request.user.username != username:
            return redirect('home')

        custom_list = get_object_or_404(CustomList,id=list_id,user=request.user)
        movie_id = request.data.get('movie_id')
        movie = get_object_or_404(Movie, id=movie_id)

        custom_list.movies.remove(movie)
        return redirect('custom_list_detail',username=username,list_id=list_id)

    def edit(self, request, username, list_id, *args, **kwargs):
        if not request.user.is_authenticated or request.user.username != username:
            return redirect('home')

        custom_list = get_object_or_404(CustomList,id=list_id,user=request.user)

        form = CustomListForm(instance=custom_list)

        return render(request, 'users/custom_list_form.html', {'form': form,'custom_list': custom_list})

    def update_list(self, request, username, list_id, *args, **kwargs):
        if not request.user.is_authenticated or request.user.username != username:
            return redirect('home')

        custom_list = get_object_or_404(CustomList,id=list_id,user=request.user)

        form = CustomListForm(request.data, instance=custom_list)

        if form.is_valid():
            form.save()
            return redirect('custom_list_detail',username=username,list_id=list_id)

        return render(request, 'users/custom_list_form.html', {'form': form,'custom_list': custom_list})

    def delete_list(self, request, username, list_id, *args, **kwargs):
        if not request.user.is_authenticated or request.user.username != username:
            return redirect('home')

        custom_list = get_object_or_404(CustomList,id=list_id,user=request.user)
        custom_list.delete()

        return redirect('user_profile',username=request.user.username)

    def all_lists(self, request, username, *args, **kwargs):
        profile_user = get_object_or_404(User, username=username)

        custom_lists = CustomList.objects.filter(user=profile_user).annotate(movie_count=Count('movies')).order_by('-created_at')

        paginator = Paginator(custom_lists, 10)
        page_obj = paginator.get_page(request.query_params.get('page'))

        return render(request, 'users/custom_list_list.html', {
            'profile_user': profile_user,
            'page_obj': page_obj
        })



class FollowViewSet(viewsets.ViewSet):

    def follow(self, request, username, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')

        user_to_follow = get_object_or_404(User, username=username)

        if request.user == user_to_follow:
            return redirect('user_profile', username=username)

        Follow.objects.get_or_create(follower=request.user,following=user_to_follow)

        return redirect('user_profile', username=username)

    def unfollow(self, request, username, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')

        user_to_unfollow = get_object_or_404(User, username=username)
        Follow.objects.filter(follower=request.user,following=user_to_unfollow).delete()

        return redirect('user_profile', username=username)

    def followers(self, request, username, *args, **kwargs):
        profile_user = get_object_or_404(User, username=username)

        followers = User.objects.filter(following__following=profile_user).order_by('username')
        if request.user.is_authenticated:
            following_ids = set(
                Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
            )

        return render(request, 'users/follow_list.html',
                      {'profile_user': profile_user,
                        'users': followers,
                        'list_type': 'followers',
                        'following_ids': following_ids
                       })

    def following(self, request, username, *args, **kwargs):
        profile_user = get_object_or_404(User, username=username)

        following = User.objects.filter(followers__follower=profile_user).order_by('username')

        if request.user.is_authenticated:
            following_ids = set(Follow.objects.filter(follower=request.user).values_list('following_id', flat=True))
        return render(request, 'users/follow_list.html',{
                    'profile_user': profile_user,
                    'users': following,
                    'list_type': 'following',
                    'following_ids': following_ids
                    })
