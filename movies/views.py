from django.contrib.sites import requests
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.utils.text import slugify
from users.models import Watchlist
from django.views import View
from users.models import CustomList
from .forms import ReviewForm
from .models import Movie, Review


class MovieListView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()

        if query:
            words = query.replace('-', ' ').split()
            movies_list = Movie.objects.all()
            for word in words:
                movies_list = movies_list.filter(title__icontains=word)
            movies_list = movies_list.order_by('-release_date')
        else:
            movies_list = Movie.objects.all().order_by('-release_date')

        paginator = Paginator(movies_list, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
            'query': query
        }

        return render(request, 'movies/movie_list.html', context)


class MovieDetailView(View):
    def get(self, request, slug, *args, **kwargs):
        movie = get_object_or_404(Movie, slug=slug)
        reviews = movie.reviews.all().order_by('-reviewed_at')

        user_has_reviewed = None
        in_watchlist = False
        user_custom_lists = []
        if request.user.is_authenticated:
            user_custom_lists = request.user.custom_lists.all()

        if request.user.is_authenticated:
            user_has_reviewed = Review.objects.filter(movie=movie, user=request.user).first()
            watchlist = Watchlist.objects.filter(user=request.user).first()
            in_watchlist = watchlist.movies.filter(pk=movie.pk).exists() if watchlist else False

        form = ReviewForm(instance=user_has_reviewed)

        return render(request, 'movies/movie_detail.html', {
            'movie': movie,
            'reviews': reviews,
            'form': form,
            'user_has_reviewed': user_has_reviewed,
            'in_watchlist': in_watchlist,
            'user_custom_lists': user_custom_lists
        })

    def post(self, request, slug, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')

        movie = get_object_or_404(Movie, slug=slug)
        user_has_reviewed = Review.objects.filter(movie=movie, user=request.user).first()

        if 'watchlist_add' in request.POST:
            watchlist, _ = Watchlist.objects.get_or_create(user=request.user)
            watchlist.movies.add(movie)
            return redirect('movie_detail', slug=movie.slug)

        if 'watchlist_remove' in request.POST:
            watchlist, _ = Watchlist.objects.get_or_create(user=request.user)
            watchlist.movies.remove(movie)
            return redirect('movie_detail', slug=movie.slug)

        if 'delete' in request.POST and user_has_reviewed:
            user_has_reviewed.delete()
            return redirect('movie_detail', slug=movie.slug)

        if 'add_to_custom_list' in request.POST:
            list_id = request.POST.get('list_id')
            if list_id:
                custom_list = get_object_or_404(CustomList, id=list_id, user=request.user)
                custom_list.movies.add(movie)
            return redirect('movie_detail', slug=movie.slug)

        form = ReviewForm(request.POST, instance=user_has_reviewed)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.user = request.user
            review.save()
            return redirect('movie_detail', slug=movie.slug)

        reviews = movie.reviews.all().order_by('-reviewed_at')
        watchlist = Watchlist.objects.filter(user=request.user).first()
        in_watchlist = watchlist.movies.filter(pk=movie.pk).exists() if watchlist else False

        return render(request, 'movies/movie_detail.html', {
            'movie': movie,
            'reviews': reviews,
            'form': form,
            'user_has_reviewed': user_has_reviewed,
            'in_watchlist': in_watchlist
        })